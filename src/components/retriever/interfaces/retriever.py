from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class Retriever(ABC):

    @abstractmethod
    def retrieve(
        self, domain_id: int, query_vector: List[float], top_n: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Retrieve top N relevant embeddings for a given domain and query vector.

        Args:
            domain_id (int): The ID of the domain within which to search for relevant embeddings.
            query_vector (List[float]): The vector representation of the user's query.
            top_n (int): The number of top relevant embeddings to retrieve.

        Returns:
            List[Tuple[int, float]]: A list of tuples, each containing an embedding's ID and its relevance score.
        """
        pass

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass
