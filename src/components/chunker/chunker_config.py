from components.chunker.fixed_length_chunker import FixedLengthChunker
from components.chunker.fixed_length_overlap_chunker import FixedLengthOverLapChunker


class ChunkerConfig:

    @property
    def chunker_options(self):
        return {
            "Fixed-Length": FixedLengthChunker,
            "Fixed-Length Overlap": FixedLengthOverLapChunker,
        }
