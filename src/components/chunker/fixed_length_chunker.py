from typing import List, Dict, Any
from .interfaces.chunker import Chunker


class FixedLengthChunker(Chunker):
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]

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
            },
            "validations": [
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
            "order": ["chunk_size"],
        }
