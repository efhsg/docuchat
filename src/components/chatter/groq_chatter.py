from functools import lru_cache
from typing import Dict, Generator, List, Tuple, Optional, Union
from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger
from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.models import ModelSource
from utils.env_utils import getenv
from transformers import AutoTokenizer
from groq import Groq


class TokenizerLoader:
    @lru_cache(maxsize=128)
    def load(self, model_identifier: str, api_token: str):
        return AutoTokenizer.from_pretrained(model_identifier, use_auth_token=api_token)


class GroqChatter(Chatter):
    def __init__(
        self,
        logger: Optional[StandardLogger] = None,
        chatter_repository: ChatterRepository = None,
        tokenizer_loader: TokenizerLoader = None,
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
        self.chatter_repository = chatter_repository
        self.tokenizer_loader = tokenizer_loader or TokenizerLoader()
        self.model_cache = self.chatter_repository.read_model_cache(
            ModelSource.Groq, self.model
        )
        self.history_truncated = False

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context: Dict[str, List[Tuple[str, float]]] = None,
    ) -> Union[str, Generator[str, None, None]]:
        windowed_messages = self._sliding_window_messages(messages if messages else [])
        try:
            stream_response = self._attempt_chat(windowed_messages)
            if self.stream:
                response = (
                    self._generate_response(stream_response)
                    if stream_response
                    else iter(["Unable to generate response."])
                )
            else:
                if not stream_response or (
                    hasattr(stream_response, "choices") and not stream_response.choices
                ):
                    if self.history_truncated and len(windowed_messages) > 1:
                        self.logger.info(
                            "Received empty response, attempting with one less message."
                        )
                        windowed_messages, _ = self._sliding_window_messages(
                            messages[:-1]
                        )
                        stream_response = self._attempt_chat(windowed_messages)
                response = (
                    stream_response.choices[0].message.content
                    if stream_response
                    and hasattr(stream_response, "choices")
                    and stream_response.choices
                    else "Unable to generate response."
                )
            return response
        except Exception as e:
            if self.logger:
                self.logger.error(f"An error occurred during chat completion: {str(e)}")
            raise

    def _attempt_chat(self, windowed_messages: List[Dict[str, str]]):
        client = Groq()
        return client.chat.completions.create(
            messages=windowed_messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            stream=self.stream,
            stop=[self.stop] if self.stop else None,
        )

    def get_num_tokens(self, text: str) -> int:
        api_token = getenv("HUGGINGFACEHUB_API_TOKEN")
        model_identifier = self.model_cache.attributes.get("huggingface_identifier")
        tokenizer = self.tokenizer_loader.load(model_identifier, api_token)
        return len(tokenizer.encode(text))

    def was_history_truncated(self) -> bool:
        """Returns True if the chat history was truncated in the last operation."""
        return self.history_truncated

    def _generate_response(self, stream_response) -> Generator[str, None, None]:
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _sliding_window_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        context_window = self.get_params().get("context_window", 4096)
        response_buffer = 256
        effective_context_window = context_window - response_buffer

        total_tokens = 0
        windowed_messages = []

        for message in reversed(messages):
            message_str = str(message)
            message_tokens = self.get_num_tokens(message_str)
            if total_tokens + message_tokens > effective_context_window:
                break
            windowed_messages.insert(0, message)
            total_tokens += message_tokens

        self.history_truncated = len(windowed_messages) < len(messages)

        if self.logger:
            self.logger.info(
                f"Total token size of windowed_messages: {total_tokens} / {effective_context_window}"
            )

        return windowed_messages

    def get_params(self) -> Dict:

        context_window = (
            self.model_cache.attributes.get("context_window")
            if self.model_cache
            else None
        )
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "stop": self.stop,
            "context_window": context_window,
        }
