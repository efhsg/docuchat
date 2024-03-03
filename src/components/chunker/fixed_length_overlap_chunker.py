from typing import List
from .interfaces.chunker import Chunker


class FixedLengthOverLapChunker(Chunker):
    def __init__(self, chunk_size: int = 1000, overlap_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size

    def chunk(self, text: str) -> List[str]:
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + self.chunk_size])
            i += self.chunk_size - self.overlap_size
        return chunks
