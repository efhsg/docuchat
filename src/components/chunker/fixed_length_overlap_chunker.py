from typing import Any, Dict, List
from .interfaces.chunker import Chunker


class FixedLengthOverLapChunker(Chunker):
    def __init__(self, chunk_size: int, overlap: int):
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
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "params": {
                "chunk_size": {
                    "label": "Chunk size",
                    "type": "number",
                    "min_value": 1,
                    "default": 1000,
                },
                "overlap": {
                    "label": "Overlap size",
                    "type": "number",
                    "min_value": 0,
                    "default": 100,
                },
            },
            "validations": [
                {
                    "rule": ("overlap", "lt", "chunk_size"),
                    "message": "Overlap must be less than Chunk size.",
                },
                {
                    "rule": (
                        "chunk_size",
                        "le",
                        "MAX_CHUNK_SIZE",
                    ),
                    "message": f"Chunk size must not exceed {Chunker.MAX_CHUNK_SIZE}.",
                },
            ],
            "constants": {"MAX_CHUNK_SIZE": Chunker.MAX_CHUNK_SIZE},
            "order": ["chunk_size", "overlap"],
        }
