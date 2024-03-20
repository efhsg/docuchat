from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Generator, Union


class Chatter(ABC):

    @abstractmethod
    def chat(
        self,
        query: Optional[str],
        context: Dict[str, List[Tuple[str, float]]],
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Union[str, Generator[str, None, None]]: ...

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass

    @abstractmethod
    def get_num_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def get_num_tokens_left(self, text: str) -> int:
        pass

    @abstractmethod
    def history_truncated_by(self) -> int:
        """Returns True if the chat history was truncated in the last operation."""
        pass
