from typing import Dict, Generator, List, Tuple, Optional, Union
from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger
from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.models import ModelSource
from utils.env_utils import getenv
from groq import Groq


class GroqChatter(Chatter):
    def __init__(
        self,
        logger: Optional[StandardLogger] = None,
        chatter_repository: ChatterRepository = None,
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

    def chat(
        self,
        messages: List[Dict[str, str]] = None,
        context: Dict[str, List[Tuple[str, float]]] = None,
    ) -> Union[str, Generator[str, None, None]]:

        client = Groq()
        stream_response = client.chat.completions.create(
            messages=messages,
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

    def get_num_tokens(self) -> int:
        return 0

    def _generate_response(self, stream_response) -> Generator[str, None, None]:
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def get_params(self) -> Dict:
        model_cache = self.chatter_repository.read_model_cache(
            ModelSource.Groq, self.model
        )
        context_window = (
            model_cache.attributes.get("context_window") if model_cache else None
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
