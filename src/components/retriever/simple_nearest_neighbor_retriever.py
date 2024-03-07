from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from components.database.models import Chunk, ChunkProcess, Embedding, ExtractedText
from .interfaces.retriever import Retriever
import pickle
from logging import Logger as StandardLogger


class SimpleNearestNeighborRetriever(Retriever):
    def __init__(
        self, session: Session, logger: StandardLogger = None, top_n: int = 5
    ) -> None:
        self.session: Session = session
        self.logger: StandardLogger = logger
        self.top_n: int = top_n

    def retrieve(
        self, domain_id: int, query_vector: List[float]
    ) -> List[Tuple[int, float]]:
        embeddings: List[Embedding] = self._fetch_embeddings(domain_id)
        embeddings_matrix: np.ndarray = self._deserialize_embeddings(embeddings)
        query_vector_array: np.ndarray = np.array(query_vector).reshape(1, -1)
        similarities: np.ndarray = self._compute_similarities(
            query_vector_array, embeddings_matrix
        )
        return self._get_top_similar_embeddings(embeddings, similarities)

    def get_configuration(self) -> dict:
        return {"method": "SimpleNearestNeighbor", "params": {"top_n": self.top_n}}

    def _fetch_embeddings(self, domain_id: int) -> List[Embedding]:
        return (
            self.session.query(Embedding)
            .join(Chunk)
            .join(ChunkProcess)
            .join(ExtractedText)
            .filter(ExtractedText.domain_id == domain_id)
            .all()
        )

    def _deserialize_embeddings(self, embeddings: List[Embedding]) -> np.ndarray:
        return np.array([pickle.loads(embedding.embedding) for embedding in embeddings])

    def _compute_similarities(
        self, query_vector: np.ndarray, embeddings_matrix: np.ndarray
    ) -> np.ndarray:
        return cosine_similarity(query_vector, embeddings_matrix).flatten()

    def _get_top_similar_embeddings(
        self, embeddings: List[Embedding], similarities: np.ndarray
    ) -> List[Tuple[int, float]]:
        top_indices: np.ndarray = np.argsort(similarities)[-self.top_n :][::-1]
        return [(embeddings[i].id, similarities[i]) for i in top_indices]
