from typing import Any, Dict, List
from .interfaces.chunker import Chunker


class FixedLengthOverLapChunker(Chunker):
    def __init__(self, name: str, chunk_size: int, overlap: int):
        self.name = name
        self.chunk_size = chunk_size
        self.overlap = overlap

    @classmethod
    def get_init_params(cls) -> List[str]:
        return ["name", "chunk_size", "overlap"]

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
                "overlap": {
                    "label": "Overlap size",
                    "type": "number",
                    "min_value": 0,
                    "default": 100,
                },
            },
        }
