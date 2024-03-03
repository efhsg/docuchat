from components.chunker.chunker_config import ChunkerConfig
from components.chunker.interfaces.chunker import Chunker
from .interfaces.chunker_factory import ChunkerFactory


class ConfigBasedChunkerFactory(ChunkerFactory):
    def create_chunker(self, method: str, **kwargs) -> Chunker:
        chunker_class = ChunkerConfig.chunker_classes.get(method)
        if not chunker_class:
            raise ValueError(f"Chunker method '{method}' is not supported.")
        return chunker_class(**kwargs)
