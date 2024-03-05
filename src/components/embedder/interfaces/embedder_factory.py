from abc import ABC, abstractmethod
from components.embedder.interfaces.embedder import Embedder


class EmbedderFactory(ABC):
    @abstractmethod
    def create_embedder(self, method: str, **kwargs) -> Embedder:
        pass
