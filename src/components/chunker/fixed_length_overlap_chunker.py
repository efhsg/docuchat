from typing import Any, Dict, List, Tuple, Union
from .interfaces.chunker import Chunker


class FixedLengthOverLapChunker(Chunker):
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + self.chunk_size])
            i += self.chunk_size - self.overlap
        return chunks

    @classmethod
    def _fields(cls) -> Dict[str, Any]:
        return {
            "chunk_size": {
                "label": "Chunk Size",
                "type": "number",
                "default": 1000,
            },
            "overlap": {
                "label": "Overlap Size",
                "type": "number",
                "default": 100,
            },
        }

    @classmethod
    def _validations(cls) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        return [
            {
                "rule": ("overlap", "lt", "chunk_size"),
                "message": "Overlap size must be less than Chunk size.",
            },
            {
                "rule": ("chunk_size", "le", cls.MAX_CHUNK_SIZE),
                "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
            },
        ]
