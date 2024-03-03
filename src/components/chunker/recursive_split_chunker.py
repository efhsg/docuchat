from typing import List, Dict, Any
from components.chunker.interfaces.chunker import Chunker
from langchain.text_splitter import RecursiveCharacterTextSplitter


class RecursiveSplitChunker(Chunker):
    def __init__(
        self, chunk_size: int = 100, overlap: int = 20, separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = (
            separators if separators is not None else ["\n\n", "\n", " ", ""]
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            length_function=len,
            is_separator_regex=False,
            separators=self.separators,
        )

    def chunk(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)
