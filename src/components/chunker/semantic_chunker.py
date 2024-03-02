import os
from typing import List, Dict, Any
from .interfaces.chunker import Chunker
import spacy


class SemanticChunker(Chunker):
    def __init__(self, model: str = "en_core_web_sm", max_chunk_size: int = 500):
        self.nlp = spacy.load(model)
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> List[str]:
        doc = self.nlp(text)
        chunks, chunk = [], ""
        for sent in doc.sents:
            if len(chunk) + len(sent.text) + 1 > self.max_chunk_size:
                chunks.append(chunk.strip())
                chunk = sent.text
            else:
                chunk += " " + sent.text
        if chunk:
            chunks.append(chunk.strip())
        return chunks

    @classmethod
    def get_chunker_options(cls) -> Dict[str, Any]:
        return {
            "fields": {
                "model": {
                    "label": "NLP Model",
                    "type": "select",
                    "default": os.getenv("CHUNKER_NLP_MODEL_DEFAULT", "en_core_web_sm"),
                    "options": os.getenv(
                        "CHUNKER_NLP_MODEL_OPTIONS",
                        "en_core_web_sm,en_core_web_md,en_core_web_lg",
                    ).split(","),
                },
                "max_chunk_size": {
                    "label": "Max Chunk Size",
                    "type": "number",
                    "default": 500,
                },
            },
            "validations": [
                {
                    "rule": ("max_chunk_size", "ge", "MIN_CHUNK_SIZE"),
                    "message": f"Chunk size must be at least {cls.MIN_CHUNK_SIZE}.",
                },
                {
                    "rule": ("max_chunk_size", "le", "MAX_CHUNK_SIZE"),
                    "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
                },
            ],
            "constants": {
                "MIN_CHUNK_SIZE": cls.MIN_CHUNK_SIZE,
                "MAX_CHUNK_SIZE": cls.MAX_CHUNK_SIZE,
            },
        }
