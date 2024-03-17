from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Generator


class Chatter(ABC):

    @abstractmethod
    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        pass

    @abstractmethod
    def chat_stream(
        self, query: str, context: Dict[str, List[Tuple[str, float]]]
    ) -> Generator[str, None, None]:
        pass

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass
