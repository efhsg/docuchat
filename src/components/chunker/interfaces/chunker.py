from abc import ABC, abstractmethod, ABCMeta
from typing import List


class Chunker(ABC, metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_init_params(cls) -> List[str]:
        pass

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass
