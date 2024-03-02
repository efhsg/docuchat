from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List, Tuple, Union


class Chunker(ABC):
    MIN_CHUNK_SIZE: int = 1
    MAX_CHUNK_SIZE: int = 100000
    MIN_OVERLAP_SIZE: int = 0

    @abstractmethod
    def chunk(self, text: str) -> List[str]: ...

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "fields": cls._fields(),
            "validations": cls._validations(),
            "constants": cls._constants(),
        }

    @classmethod
    def _fields(cls) -> Dict[str, Any]:
        return {}

    @classmethod
    def _validations(cls) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        return []

    @classmethod
    def _constants(cls) -> Dict[str, int]:
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }

    @staticmethod
    def getenv(
        param: str, default: str = "", separator: str = ","
    ) -> Union[str, List[str]]:
        value = os.getenv(param, default)
        return value.split(separator) if separator in value else value
