from abc import ABC, abstractmethod
from typing import Any


class ChatterFactory(ABC):
    @abstractmethod
    def create_chatter(self, method: str, **kwargs) -> Any:
        """
        Create and return an instance of a Chatter based on the specified method.

        Args:
            method (str): The chat method identifier.
            **kwargs: Additional keyword arguments to pass to the chatter's constructor.

        Returns:
            An instance of a Chatter.
        """
        pass
