from typing import List, Dict, Any
from .interfaces.chunker import Chunker


class FixedLengthChunker(Chunker):
    def __init__(self, name: str, chunk_size: int):
        self.name = name
        self.chunk_size = chunk_size

    @classmethod
    def get_init_params(cls) -> List[str]:
        return ["name", "chunk_size"]

    def chunk(self, text: str) -> List[str]:
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "params": {
                "name": {
                    "label": "Name",
                    "type": "string",
                    "default": "",
                },
                "chunk_size": {
                    "label": "Chunk size",
                    "type": "number",
                    "min_value": 1,
                    "default": 1000,
                },
            },
        }
