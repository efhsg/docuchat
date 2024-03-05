from .embedder_config import EmbedderConfig
from .interfaces.embedder import Embedder
from .interfaces.embedder_factory import EmbedderFactory


class ConfigBasedEmbedderFactory(EmbedderFactory):
    def create_embedder(self, method: str, **kwargs) -> Embedder:
        embedder_class = EmbedderConfig.embedder_classes.get(method)
        if not embedder_class:
            raise ValueError(f"Embedder method '{method}' is not supported.")
        return embedder_class(**kwargs)
