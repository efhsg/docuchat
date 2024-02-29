from typing import Dict, Any
from .fixed_length_overlap_chunker import FixedLengthOverLapChunker
from .fixed_length_chunker import FixedLengthChunker


class ChunkerConfig:
    @property
    def chunker_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            "Fixed-Length": {
                "class": FixedLengthChunker,
                **FixedLengthChunker.get_chunker_options(),
            },
            "Fixed-Length Overlap": {
                "class": FixedLengthOverLapChunker,
                **FixedLengthOverLapChunker.get_chunker_options(),
            },
        }
