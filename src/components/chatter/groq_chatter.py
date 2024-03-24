from typing import Dict, Generator, List, Optional, Union
from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger
from components.chatter.interfaces.chatter_repository import ChatterRepository
from groq import Groq


class GroqChatter(Chatter):
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

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
    ) -> Union[str, Generator[str, None, None]]:

        reduced_messages, _, num_tokens_reduced_messages = (
            self.chat_text_processor.reduce_texts(
                messages=(messages if messages else []),
            )
        )
        self.history_truncated = len(messages) - len(reduced_messages)
        self.check_token_size(messages, reduced_messages, num_tokens_reduced_messages)

        client = Groq()
        try:
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
                return stream_response.choices[0].message.content
            else:
                return self._generate_response(stream_response)

        except Exception as e:
            if self.logger:
                self.logger.error(f"An error occurred during chat completion: {str(e)}")
            raise

    def get_num_tokens(self, text: str) -> int:
        self.chat_text_processor.get_num_tokens(
            text=text,
        )

    def get_num_tokens_left(self, messages: List[Dict[str, str]]) -> int:
        return self.chat_text_processor.get_num_tokens_left(messages=messages)

    def history_truncated_by(self) -> int:
        return self.history_truncated

    def check_token_size(self, messages, reduced_messages, num_tokens_reduced_messages):
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
                yield chunk.choices[0].delta.content

    def get_params(self) -> Dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "stop": self.stop,
            "context_window": self.chat_text_processor.context_window,
        }
