from components.chatter.interfaces.chatter import Chatter
from components.chatter.chatter_config import ChatterConfig
from logging import Logger as StandardLogger

from components.chatter.interfaces.chatter_repository import ChatterRepository
from .interfaces.chatter_factory import ChatterFactory


class ConfigBasedChatterFactory(ChatterFactory):
    def __init__(
        self,
        logger: StandardLogger = None,
        chatter_repository: ChatterRepository = None,
    ):
        self.logger = logger
        self.chatter_repository = chatter_repository

    def create_chatter(self, method: str, **kwargs) -> Chatter:
        chatter_config = ChatterConfig.chatter_classes.get(method)
        if not chatter_config:
            if self.logger:
                self.logger.error(f"Chatter method '{method}' is not supported.")
            raise ValueError(f"Chatter method '{method}' is not supported.")

        chatter_class = chatter_config["class"]
        chat_text_processor = chatter_config.get("chat_text_processor")

        return chatter_class(
            logger=self.logger,
            chatter_repository=self.chatter_repository,
            chat_text_processor=chat_text_processor,
            **kwargs,
        )
