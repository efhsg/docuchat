import os
import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from logging import Logger as StandardLogger
from .interfaces.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    def __init__(
        self,
        model: str = "all-mpnet-base-v2",
        logger: StandardLogger = None,
        model_cache_dir: str = "./data/models",
    ):
        self.model_name = model
        model_path = os.path.join(model_cache_dir, model)
        self.logger = logger
        try:
            if os.path.exists(model_path):
                self.model = SentenceTransformer(model_path)
            else:
                self.model = SentenceTransformer(model)
                self.logger.info(f"Save to cache: {model_path}")
                os.makedirs(model_cache_dir, exist_ok=True)
                self.model.save(model_path)
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to download or load the SentenceTransformer model '{model}'. Error: {e}"
                )
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
