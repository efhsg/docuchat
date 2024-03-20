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
    def load(self, model_identifier: str) -> AutoTokenizer:
        api_token = getenv("HUGGINGFACEHUB_API_TOKEN")
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
        self.history_truncated: int = 0
        self.context_window = self.get_params().get("context_window", 4096)

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context: Dict[str, List[Tuple[str, float]]] = None,
    ) -> Union[str, Generator[str, None, None]]:

        windowed_messages, total_tokens = self._sliding_window_messages(
            messages if messages else []
        )
        client = Groq()
        try:
            stream_response = client.chat.completions.create(
                messages=windowed_messages,
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
        tokenizer = self.tokenizer_loader.load(
            self.model_cache.attributes.get("huggingface_identifier")
        )
        return len(tokenizer.encode(text))

    def get_num_tokens_left(self, messages: List[Dict[str, str]]) -> int:
        _, total_used_tokens = self._sliding_window_messages(messages)
        return self.context_window - total_used_tokens

    def history_truncated_by(self) -> int:
        return self.history_truncated

    def _generate_response(self, stream_response) -> Generator[str, None, None]:
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _sliding_window_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        response_buffer = 512
        effective_context_window = self.context_window - response_buffer

        total_tokens = 0
        windowed_messages = []

        for message in reversed(messages):
            message_str = str(message)
            message_tokens = self.get_num_tokens(message_str)
            if total_tokens + message_tokens > effective_context_window:
                break
            windowed_messages.insert(0, message)
            total_tokens += message_tokens

        self.history_truncated = len(messages) - len(windowed_messages)

        return windowed_messages, total_tokens

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
