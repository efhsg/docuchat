from abc import ABC, abstractmethod
from components.chunker.interfaces.chunker import Chunker


class ChunkerFactory(ABC):
    @abstractmethod
    def create_chunker(self, method: str, **kwargs) -> Chunker:
        pass
