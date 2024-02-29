from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Chunker(ABC):

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        pass
