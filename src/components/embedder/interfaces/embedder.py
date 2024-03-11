from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class Embedder(ABC):

    @abstractmethod
    def embed(self, chunks: List[Tuple[int, str]]) -> List[Tuple[int, List[float]]]:
        pass
        """Generate embeddings for a list of chunk texts, each identified by its ID.

        Args:
            chunks (List[Tuple[int, str]]): A list of tuples, where each tuple contains a chunk's  ID and its text.

        Returns:
            List[Tuple[int, List[float]]]: A list of tuples, where each tuple contains a chunk's ID and its embedding as a list of floats.
        """

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass
