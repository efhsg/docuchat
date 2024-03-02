from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Chunker(ABC):

    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 100000

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        pass
