from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Chunker(ABC):
    @classmethod
    @abstractmethod
    def get_init_params(cls) -> List[str]:
        pass

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        pass
