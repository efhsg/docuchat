from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List, Union, Tuple


class Chunker(ABC):
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 100000

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "fields": cls._fields(),
            "validations": cls._validations(),
            "constants": cls._constants(),
        }

    @classmethod
    def _fields(cls) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def _validations(cls) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        raise NotImplementedError

    @classmethod
    def _constants(cls) -> Dict[str, Dict[str, int]]:
        return {
            "MIN_CHUNK_SIZE": cls.MIN_CHUNK_SIZE,
            "MAX_CHUNK_SIZE": cls.MAX_CHUNK_SIZE,
        }

    @staticmethod
    def getenv(
        param: str, default: str = "", separator: str = ","
    ) -> Union[str, List[str]]:
        value = os.getenv(param, default)
        if separator in value:
            return value.split(separator)
        return value
