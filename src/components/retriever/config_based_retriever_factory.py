from components.database.interfaces.connector import Connector
from .interfaces.retriever import Retriever
from .interfaces.retriever_factory import RetrieverFactory
from .retriever_config import RetrieverConfig
from logging import Logger as StandardLogger


class ConfigBasedRetrieverFactory(RetrieverFactory):
    def __init__(
        self,
        connector: Connector = None,
        logger: StandardLogger = None,
    ):
        self.session = connector.get_session()
        self.logger = logger

    def create_retriever(self, method: str, **kwargs) -> Retriever:
        retriever_class = RetrieverConfig.retriever_classes.get(method)
        if not retriever_class:
            raise ValueError(f"Retriever method '{method}' is not supported.")
        return retriever_class(session=self.session, logger=self.logger, **kwargs)
