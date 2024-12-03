from typing import _TypedDict, Dict, Generator, List, Literal, Optional, Tuple, Union
from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from components.chatter.interfaces.chatter_repository import ChatterRepository
from groq import Groq

from utils.logger_utils import log_to_json


class Message(_TypedDict, total=False):
    role: Union[Literal["user"], Literal["system"], Literal["assistant"]]
    content: str
    name: Optional[str]
    seed: Optional[int]


class GroqChatter(Chatter):

    INSTRUCTIONS = """
Instructions:
- Be helpful and answer questions concisely. If you don't know the answer, say 'I don't know'.
- Utilize the context provided for accurate and specific information.
- Incorporate your preexisting knowledge to enhance the depth and relevance of your response.
"""

    def __init__(
        self,
        logger: Optional[StandardLogger] = None,
        chat_text_processor: ChatTextProcessor = None,
        groq_model: str = "llama2-70b-4096",
        temperature: float = 0.5,
        max_tokens: int = 1024,
        top_p: float = 1,
        stream: bool = True,
        stop: Optional[str] = None,
    ):
        self.model = groq_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop
        self.logger = logger
        self.chat_text_processor = chat_text_processor
        self.history_truncated: int = 0
        self.context_truncated: int = 0
        self.total_tokens_used: int = 0

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
        dry_run: bool = False,
    ) -> Union[str, Generator[str, None, None]]:

        reduced_messages = self._reduce_messages(messages, context_texts)

        self.logger.info(self.get_num_tokens(str(reduced_messages)))
        # self.logger.debug(log_to_json(reduced_messages))

        try:
            if dry_run:
                if not self.stream:
                    return "mock"
                else:

                    def mock_generator():
                        yield "mock"

                    return mock_generator()
            else:
                client = Groq()
                stream_response = client.chat.completions.create(
                    messages=reduced_messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    stream=self.stream,
                    stop=[self.stop] if self.stop else None,
                )

                if not self.stream:
                    self.total_tokens_used += self.get_num_tokens(
                        stream_response.choices[0].message.content
                    )
                    return stream_response.choices[0].message.content
                else:
                    return self._generate_response(stream_response)

        except Exception as e:
            if self.logger:
                self.logger.error(f"An error occurred during chat completion: {str(e)}")
            raise

    def _reduce_messages(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
        preserve_state: bool = True,
    ):
        api_messages = self.convert_messages_for_api(messages)

        reduced_messages, reduced_context_texts, total_tokens_used = (
            self.chat_text_processor.reduce_texts(
                messages=(api_messages if api_messages else []),
                context_texts=context_texts,
            )
        )

        if preserve_state:
            self._check_token_size(api_messages, reduced_messages, total_tokens_used)
            self.history_truncated = len(api_messages) - len(reduced_messages)
            self.context_truncated = len(context_texts) - len(reduced_context_texts)
            self.total_tokens_used = total_tokens_used

        if reduced_context_texts:
            reduced_messages.append(self._format_system_message(reduced_context_texts))

        return reduced_messages

    def get_num_tokens(self, text: Optional[str]) -> int:
        if not text:
            return 0
        try:
            return self.chat_text_processor.get_num_tokens(text)
        except Exception as e:
            self.logger.error(f"Error encoding text in get_num_tokens: {e}")
            return 0

    def get_num_tokens_left(self, messages: List[Dict[str, str]]) -> int:
        return self.chat_text_processor.get_num_tokens_left(messages=messages)

    def history_truncated_by(self) -> int:
        return self.history_truncated

    def context_truncated_by(self) -> int:
        return self.context_truncated

    def get_total_tokens_used(self) -> int:
        return self.total_tokens_used

    def calculate_total_tokens(
        self, messages: List[Dict[str, str]] = None, context_texts: List[str] = None
    ) -> int:
        other_messages, most_recent_ai_message_content = (
            self._separate_most_recent_ai_message(messages)
        )
        reduced_other_messages = str(
            self._reduce_messages(
                messages=other_messages,
                context_texts=context_texts,
                preserve_state=False,
            )
        )
        total_string = f"{reduced_other_messages}{most_recent_ai_message_content}"
        total_tokens = self.get_num_tokens(
            reduced_other_messages + most_recent_ai_message_content
        )

        self.logger.info(f"{total_string} : {total_tokens}")
        return total_tokens

    def _separate_most_recent_ai_message(
        self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    ) -> Tuple[List[Union[HumanMessage, AIMessage, SystemMessage]], str]:
        if not messages:
            return [], ""
        messages_clone = messages[:]
        most_recent_ai_message_content = ""
        for i in reversed(range(len(messages_clone))):
            message = messages_clone[i]
            if isinstance(message, AIMessage):
                most_recent_ai_message_content = message.content
                messages_clone.pop(i)
                break
        return messages_clone, most_recent_ai_message_content

    def _check_token_size(
        self, messages, reduced_messages, num_tokens_reduced_messages
    ):
        if (
            len(reduced_messages) == 0
            or self.get_num_tokens_left(messages=reduced_messages) <= 0
        ):
            tokens = (
                num_tokens_reduced_messages
                if num_tokens_reduced_messages > 0
                else self.chat_text_processor.get_num_tokens(str(messages))
            )
            error_message = f"Insufficient tokens left to proceed with chat completion. Message size already {tokens} tokens."
            if self.logger:
                self.logger.error(error_message)
            raise ValueError(error_message)

    def _generate_response(self, stream_response) -> Generator[str, None, None]:
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                self.total_tokens_used += self.get_num_tokens(
                    chunk.choices[0].delta.content
                )
                yield chunk.choices[0].delta.content

    def get_params(self) -> Dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "stop": self.stop,
            "context_window": (
                getattr(self.chat_text_processor, "context_window", 0)
                if self.chat_text_processor is not None
                else 0
            ),
        }

    def convert_messages_for_api(
        self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    ) -> List[Message]:
        message_type_to_role = {
            HumanMessage: "user",
            AIMessage: "assistant",
            SystemMessage: "system",
        }

        prepared_messages = []
        for message in messages:
            role = message_type_to_role.get(type(message))
            if not role:
                raise ValueError(f"Unsupported message type: {type(message).__name__}")

            prepared_message: Message = {"role": role, "content": message.content}

            if hasattr(message, "name") and message.name is not None:
                prepared_message["name"] = message.name
            if hasattr(message, "seed") and message.seed is not None:
                prepared_message["seed"] = message.seed

            prepared_messages.append(prepared_message)
        return prepared_messages

    def _sys_prompt(self, context_texts: List[str]) -> str:
        full_prompt = f"{GroqChatter.INSTRUCTIONS}\nContext: {" ".join(context_texts)}"
        return self.sanitize_text_for_json(full_prompt)

    def _format_system_message(self, reduced_context_texts):
        return {"role": "system", "content": self._sys_prompt(reduced_context_texts)}
