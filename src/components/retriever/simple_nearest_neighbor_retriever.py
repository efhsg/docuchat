from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func
from sqlalchemy.orm import Session
from components.database.models import (
    Chunk,
    ChunkProcess,
    Embedding,
    EmbeddingProcess,
    ExtractedText,
)
from components.embedder.interfaces.embedder import Embedder
from .interfaces.retriever import Retriever
import pickle
from logging import Logger as StandardLogger


class SimpleNearestNeighborRetriever(Retriever):
    def __init__(
        self,
        session: Session,
        logger: StandardLogger = None,
        domain_id: int = None,
        text_ids: List[int] = None,
        embedder_config: Dict = None,
        top_n: int = 5,
    ) -> None:
        self.session = session
        self.logger = logger
        self.domain_id = domain_id
        self.text_ids = text_ids
        self.top_n = top_n

        if embedder_config:
            self.embedder_method = embedder_config.get("method")
            self.embedder_model = embedder_config.get("params", {}).get("model")
        else:
            self.embedder_method = None
            self.embedder_model = None

    def retrieve(
        self,
        query_vector: List[float],
    ) -> List[Tuple[int, float]]:
        embeddings = self._fetch_embeddings()
        if not embeddings:
            return []

        embeddings_matrix = self._deserialize_embeddings(embeddings)
        if embeddings_matrix.shape[1] != len(query_vector):
            error_msg = f"Incompatible dimension for query vector and embeddings matrix: {len(query_vector)} vs {embeddings_matrix.shape[1]}"
            if self.logger:
                self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        query_vector_array = np.array(query_vector).reshape(1, -1)
        similarities = self._compute_similarities(query_vector_array, embeddings_matrix)

        return self._get_top_similar_embeddings(embeddings, similarities)

    def get_params(self) -> Dict:
        return {"top_n": self.top_n}

    def _fetch_embeddings(self) -> List[Embedding]:
        query = (
            self.session.query(Embedding)
            .join(Chunk)
            .join(ChunkProcess)
            .join(
                EmbeddingProcess, EmbeddingProcess.id == Embedding.embedding_process_id
            )
            .join(ExtractedText)
            .filter(ExtractedText.domain_id == self.domain_id)
        )
        if self.text_ids is not None:
            query = query.filter(ExtractedText.id.in_(self.text_ids))
        if self.embedder_method is not None:
            query = query.filter(EmbeddingProcess.method == self.embedder_method)
        if self.embedder_model is not None:
            query = query.filter(
                func.JSON_EXTRACT(EmbeddingProcess.parameters, "$.model")
                == self.embedder_model
            )
        return query.all()

    def _deserialize_embeddings(self, embeddings: List[Embedding]) -> np.ndarray:
        return np.array([pickle.loads(embedding.embedding) for embedding in embeddings])

    def _compute_similarities(
        self, query_vector: np.ndarray, embeddings_matrix: np.ndarray
    ) -> np.ndarray:
        return cosine_similarity(query_vector, embeddings_matrix).flatten()

    def _get_top_similar_embeddings(
        self, embeddings: List[Embedding], similarities: np.ndarray
    ) -> List[Tuple[int, float]]:
        top_indices = np.argsort(similarities)[-self.top_n :][::-1]
        return [(embeddings[i].id, similarities[i]) for i in top_indices]
