from abc import ABC, abstractmethod
from components.retriever.interfaces.retriever import Retriever


class RetrieverFactory(ABC):
    @abstractmethod
    def create_retriever(self, method: str, **kwargs) -> Retriever:
        """
        Create and return an instance of a Retriever based on the specified method.

        Args:
            method (str): The retrieval method identifier.
            **kwargs: Additional keyword arguments to pass to the retriever's constructor.

        Returns:
            Retriever: An instance of a Retriever.
        """
        pass
