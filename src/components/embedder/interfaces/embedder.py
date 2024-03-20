from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

import numpy as np


class Embedder(ABC):

    @abstractmethod
    def embed_chunks(
        self, chunks: List[Tuple[int, str]]
    ) -> List[Tuple[int, List[float]]]:
        """Generate embeddings for a list of chunk texts, each identified by its ID.

        Args:
            chunks (List[Tuple[int, str]]): A list of tuples, where each tuple contains a chunk's  ID and its text.

        Returns:
            List[Tuple[int, List[float]]]: A list of tuples, where each tuple contains a chunk's ID and its embedding as a list of floats.
        """
        pass

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single user query and returns the numpy array directly.

        :param text: The user query as a string.
        :return: The embedding of the user query as a numpy array.
        """
        pass

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass
