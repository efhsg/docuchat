from typing import List, Dict, Any
from components.chunker.interfaces.chunker import Chunker
from langchain.text_splitter import RecursiveCharacterTextSplitter


class RecursiveSplitChunker(Chunker):
    def __init__(self, chunk_size: int, overlap: int, separators: List[str] = None):
        if separators is None:
            separators = [
                "\n\n",
                "\n",
                " ",
                "",
            ]
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
            separators=separators,
        )

    def chunk(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "params": {
                "chunk_size": {
                    "label": "Chunk size",
                    "type": "number",
                    "min_value": 1,
                    "default": 100,
                },
                "overlap": {
                    "label": "Overlap size",
                    "type": "number",
                    "min_value": 0,
                    "default": 20,
                },
                "separators": {
                    "label": "Separators",
                    "type": "list",
                    "default": ["\n\n", "\n", " ", ""],
                },
            },
            "validations": [
                {
                    "rule": ("overlap", "lt", "chunk_size"),
                    "message": "Overlap must be less than Chunk size.",
                },
            ],
            "constants": {},
            "order": ["chunk_size", "overlap", "separators"],
        }
