from typing import List, Dict, Any
from utils.env_utils import getenv
from .interfaces.chunker import Chunker
import spacy


class SemanticChunker(Chunker):
    def __init__(self, model: str = "en_core_web_sm", chunk_size: int = 500):
        self.nlp = spacy.load(model)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        doc = self.nlp(text)
        chunks, chunk = [], ""
        for sent in doc.sents:
            if len(chunk) + len(sent.text) + 1 > self.chunk_size:
                chunks.append(chunk.strip())
                chunk = sent.text
            else:
                chunk += " " + sent.text
        if chunk:
            chunks.append(chunk.strip())
        return chunks
