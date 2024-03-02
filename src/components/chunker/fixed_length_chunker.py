from typing import List, Dict, Any, Tuple, Union
from .interfaces.chunker import Chunker


class FixedLengthChunker(Chunker):
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]

    @classmethod
    def _fields(cls) -> Dict[str, Any]:
        return {
            "chunk_size": {
                "label": "Chunk Size",
                "type": "number",
                "default": 1000,
            },
        }

    @classmethod
    def _validations(cls) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        return [
            {
                "rule": ("chunk_size", "ge", cls.MIN_CHUNK_SIZE),
                "message": f"Chunk size must be at least {cls.MIN_CHUNK_SIZE}.",
            },
            {
                "rule": ("chunk_size", "le", cls.MAX_CHUNK_SIZE),
                "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
            },
        ]
