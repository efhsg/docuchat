from typing import List
from .interfaces.chunker import Chunker


class FixedLengthOverLapChunker(Chunker):
    def __init__(self, name: str, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    @classmethod
    def get_init_params(cls):
        return ["chunk_size", "overlap"]

    def chunk(self, text: str) -> List[str]:
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + self.chunk_size])
            i += self.chunk_size - self.overlap
        return chunks
