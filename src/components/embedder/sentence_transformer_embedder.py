import pickle
import base64
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from .interfaces.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model)

    def embed(self, chunks: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        chunk_ids, texts = zip(*chunks)
        embeddings = self.model.encode(
            texts, convert_to_tensor=False, show_progress_bar=True
        )
        serialized_embeddings = [
            base64.b64encode(pickle.dumps(embedding)).decode("utf-8")
            for embedding in embeddings
        ]
        return list(zip(chunk_ids, serialized_embeddings))
