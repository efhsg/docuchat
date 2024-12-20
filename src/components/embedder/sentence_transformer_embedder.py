import os
import pickle
from typing import Dict, List, Tuple
import numpy as np
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
        self.logger = logger
        self.model = self.initialize_model(model, model_cache_dir)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()

    def initialize_model(self, model: str, model_cache_dir: str) -> SentenceTransformer:
        model_path = os.path.join(model_cache_dir, model)
        try:
            if os.path.exists(model_path):
                model_instance = SentenceTransformer(model_path)
            else:
                model_instance = SentenceTransformer(model)
                os.makedirs(model_cache_dir, exist_ok=True)
                model_instance.save(model_path)
            return model_instance
        except Exception as e:
            self.log_error(model, e)
            raise RuntimeError(
                f"Failed to download or load the model '{model}'. Error: {e}"
            )

    def log_error(self, model: str, error: Exception):
        if self.logger:
            self.logger.error(
                f"Failed to download or load the SentenceTransformer model '{model}'. Error: {error}"
            )

    def embed_chunks(self, chunks: List[Tuple[int, str]]) -> List[Tuple[int, bytes]]:
        chunk_ids, texts = zip(*chunks)
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        embeddings_np = embeddings.cpu().numpy().astype(np.float32)
        serialized_embeddings = [pickle.dumps(embedding) for embedding in embeddings_np]
        return list(zip(chunk_ids, serialized_embeddings))

    def embed_text(self, text: str) -> np.ndarray:
        embeddings = self.model.encode([text], convert_to_tensor=True)
        embeddings_np = embeddings.cpu().numpy().astype(np.float32)
        return embeddings_np[0]

    def get_params(self) -> Dict:
        return {
            "model": self.model_name,
            "embedding_dimension": self.embedding_dimension,
        }
