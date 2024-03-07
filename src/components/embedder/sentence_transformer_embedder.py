import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from .interfaces.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model_name = model
        try:
            self.model = SentenceTransformer(model)
        except Exception as e:
            raise RuntimeError(
                f"Failed to download or load the SentenceTransformer model '{model}'. Error: {e}"
            )

    def embed(self, chunks: List[Tuple[int, str]]) -> List[Tuple[int, bytes]]:
        chunk_ids, texts = zip(*chunks)
        embeddings = self.model.encode(
            texts, convert_to_tensor=False, show_progress_bar=True
        )
        serialized_embeddings = [pickle.dumps(embedding) for embedding in embeddings]
        return list(zip(chunk_ids, serialized_embeddings))

    def get_configuration(self) -> dict:
        return {"method": "SentenceTransformer", "params": {"model": self.model_name}}
