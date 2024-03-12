from components.chatter.interfaces.chatter import Chatter
from components.chatter.chatter_config import ChatterConfig
from logging import Logger as StandardLogger

from components.database.interfaces.connector import Connector
from .interfaces.chatter_factory import ChatterFactory


class ConfigBasedChatterFactory(ChatterFactory):
    def __init__(
        self,
        logger: StandardLogger = None,
    ):
        self.logger = logger

    def create_chatter(self, method: str, **kwargs) -> Chatter:
        chatter_class = ChatterConfig.chatter_classes.get(method)
        if not chatter_class:
            if self.logger:
                self.logger.error(f"Chatter method '{method}' is not supported.")
            raise ValueError(f"Chatter method '{method}' is not supported.")

        return chatter_class(logger=self.logger, **kwargs)
