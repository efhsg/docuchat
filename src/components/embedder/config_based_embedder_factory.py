from .embedder_config import EmbedderConfig
from .interfaces.embedder import Embedder
from .interfaces.embedder_factory import EmbedderFactory
from logging import Logger as StandardLogger


class ConfigBasedEmbedderFactory(EmbedderFactory):
    def __init__(self, logger: StandardLogger = None, model_cache_dir: str = None):
        self.logger = logger
        self.model_cache_dir = model_cache_dir

    def create_embedder(self, method: str, **kwargs) -> Embedder:
        self.logger.info(self.model_cache_dir)
        embedder_class = EmbedderConfig.embedder_classes.get(method)
        if not embedder_class:
            raise ValueError(f"Embedder method '{method}' is not supported.")
        return embedder_class(
            logger=self.logger, model_cache_dir=self.model_cache_dir, **kwargs
        )
