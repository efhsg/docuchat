from typing import Dict, Any
from components.chunker.interfaces.chunker import Chunker

from .semantic_chunker import SemanticChunker
from .fixed_length_overlap_chunker import FixedLengthOverLapChunker
from .fixed_length_chunker import FixedLengthChunker
from .recursive_split_chunker import RecursiveSplitChunker


class ChunkerConfig:
    chunker_classes: Dict[str, Chunker] = {
        "Fixed-Length": FixedLengthChunker,
        "Fixed-Length Overlap": FixedLengthOverLapChunker,
        "Recursive Split": RecursiveSplitChunker,
        "Semantic": SemanticChunker,
    }

    @property
    def chunker_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {"class": cls, **cls.get_chunker_options()}
            for name, cls in self.chunker_classes.items()
        }
