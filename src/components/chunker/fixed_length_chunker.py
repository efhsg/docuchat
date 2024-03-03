from typing import List
from .interfaces.chunker import Chunker


class FixedLengthChunker(Chunker):
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]
