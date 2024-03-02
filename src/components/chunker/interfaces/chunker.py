from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List, Union


class Chunker(ABC):

    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 100000

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

    @staticmethod
    def getenv(
        param: str, default: str = "", separator: str = ","
    ) -> Union[str, List[str]]:
        value = os.getenv(param, default)
        if separator in value:
            return value.split(separator)
        return value

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "constants": {
                "MIN_CHUNK_SIZE": cls.MIN_CHUNK_SIZE,
                "MAX_CHUNK_SIZE": cls.MAX_CHUNK_SIZE,
            }
        }
