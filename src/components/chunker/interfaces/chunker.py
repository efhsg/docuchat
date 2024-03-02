from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union


class Chunker(ABC):
    MIN_CHUNK_SIZE: int = 1
    MAX_CHUNK_SIZE: int = 100000
    MIN_OVERLAP_SIZE: int = 0

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
        return {}

    @classmethod
    def _validations(cls) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        validations = []
        fields = cls._fields()
        if "chunk_size" in fields:
            validations.extend(
                [
                    {
                        "rule": ("chunk_size", "ge", cls.MIN_CHUNK_SIZE),
                        "message": f"Chunk size must be at least {cls.MIN_CHUNK_SIZE}.",
                    },
                    {
                        "rule": ("chunk_size", "le", cls.MAX_CHUNK_SIZE),
                        "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
                    },
                ]
            )
        if "overlap" in fields:
            validations.extend(
                [
                    {
                        "rule": ("overlap", "ge", cls.MIN_OVERLAP_SIZE),
                        "message": f"Overlap size must be at least {cls.MIN_OVERLAP_SIZE}.",
                    },
                    {
                        "rule": ("overlap", "lt", "chunk_size"),
                        "message": "Overlap size must be less than Chunk size.",
                    },
                ]
            )
        return validations

    @classmethod
    def _constants(cls) -> Dict[str, int]:
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }
