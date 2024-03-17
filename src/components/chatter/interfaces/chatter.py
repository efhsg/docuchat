from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Generator, Union


class Chatter(ABC):

    @abstractmethod
    def chat(
        self,
        query: str,
        context: Dict[str, List[Tuple[str, float]]],
    ) -> Union[str, Generator[str, None, None]]: ...

    def get_configuration(self) -> Dict:
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        pass
