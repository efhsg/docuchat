import tensorflow_hub as hub
import pickle
from typing import List, Tuple
from logging import Logger as StandardLogger
from .interfaces.embedder import Embedder


class UniversalSentenceEncoderEmbedder(Embedder):
    def __init__(
        self,
        model_url: str = "https://tfhub.dev/google/universal-sentence-encoder/4",
        logger: StandardLogger = None,
        model_cache_dir: str = "./data/models",
    ):
        self.model_url = model_url
        self.logger = logger
        self.model_cache_dir = model_cache_dir
        self.model = self.load_model()

    def load_model(self):
        try:
            model = hub.load(self.model_url)
            if self.logger:
                self.logger.info(
                    f"Universal Sentence Encoder loaded from {self.model_url}"
                )
            return model
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to load the Universal Sentence Encoder model from '{self.model_url}'. Error: {e}"
                )
            raise RuntimeError(
                f"Failed to load the Universal Sentence Encoder model from '{self.model_url}'. Error: {e}"
            )

    def embed(self, chunks: List[Tuple[int, str]]) -> List[Tuple[int, bytes]]:
        _, texts = zip(*chunks)
        embeddings = self.model(texts)
        serialized_embeddings = [
            pickle.dumps(embedding.numpy()) for embedding in embeddings
        ]
        return list(zip([chunk[0] for chunk in chunks], serialized_embeddings))

    def get_configuration(self) -> dict:
        return {
            "method": "UniversalSentenceEncoder",
            "params": {"model_url": self.model_url},
        }
