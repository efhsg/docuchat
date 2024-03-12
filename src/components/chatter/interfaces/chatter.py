from abc import ABC, abstractmethod
from typing import Dict, Tuple, List


class Chatter(ABC):

    @abstractmethod
    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        """
        Generate a response to a user's query based on the given context.

        Args:
            query (str): The user's input query.
            context (Dict[str, List[Tuple[str, float]]]): The current conversation context,
            possibly including past queries and their relevance scores.

        Returns:
            str: The generated response.
        """
        pass

    def get_configuration(self) -> Dict:
        """
        Returns the configuration of the chatter instance.

        Returns:
            Dict: A dictionary containing the method name and its parameters.
        """
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        """
        Returns the parameters of the chatter instance.

        Returns:
            Dict: A dictionary of parameters.
        """
        pass
