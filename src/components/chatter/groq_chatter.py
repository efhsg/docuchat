from typing import Dict, Generator, List, Optional, Union
from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger
from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.models import ModelSource
from groq import Groq


class GroqChatter(Chatter):
    def __init__(
        self,
        logger: Optional[StandardLogger] = None,
        chatter_repository: ChatterRepository = None,
        chat_text_processor: ChatTextProcessor = None,
        groq_model: str = "llama2-70b-4096",
        temperature: float = 0.5,
        max_tokens: int = 1024,
        top_p: float = 1,
        stream: bool = True,
        stop: Optional[str] = None,
        huggingface_identifier: str = None,
        context_window: int = 4096,
    ):
        self.model = groq_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop
        self.logger = logger
        self.chatter_repository = chatter_repository
        self.huggingface_identifier = huggingface_identifier
        self.chat_text_processor = chat_text_processor
        self.history_truncated: int = 0
        self.context_window = context_window

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
    ) -> Union[str, Generator[str, None, None]]:

        reduced_messages, _, _ = self.chat_text_processor.reduce_texts(
            messages=(messages if messages else []),
            identifier=self.huggingface_identifier,
        )
        self.history_truncated = len(messages) - len(reduced_messages)

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
            identifier=self.huggingface_identifier,
        )

    def get_num_tokens_left(self, messages: List[Dict[str, str]]) -> int:
        _, _, total_used_tokens = self.chat_text_processor.reduce_texts(
            messages=messages,
            context_window=self.context_window,
            identifier=self.huggingface_identifier,
        )
        return self.context_window - total_used_tokens

    def history_truncated_by(self) -> int:
        return self.history_truncated

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
            "context_window": self.context_window,
        }
