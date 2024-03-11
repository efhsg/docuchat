import faiss
import numpy as np
from typing import List, Tuple, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session
from components.database.models import (
    Chunk,
    ChunkProcess,
    Embedding,
    EmbeddingProcess,
    ExtractedText,
)
from .interfaces.retriever import Retriever
import pickle
from logging import Logger as StandardLogger


class FAISSRetriever(Retriever):
    def __init__(
        self,
        session: Session,
        logger: StandardLogger = None,
        domain_id: int = None,
        text_ids: List[int] = None,
        embedder_config: Dict = None,
        top_n: int = 5,
        embedding_dim: int = 768,
        lambda_param: float = 0.01,
    ) -> None:
        self.session = session
        self.logger = logger
        self.domain_id = domain_id
        self.text_ids = text_ids
        self.top_n = top_n
        self.embedding_dim = embedding_dim
        self.lambda_param = lambda_param

        if embedder_config:
            self.embedder_method = embedder_config.get("method")
            self.embedder_model = embedder_config.get("params", {}).get("model")
        else:
            self.embedder_method = None
            self.embedder_model = None

        self.index = faiss.IndexFlatL2(self.embedding_dim)

    def retrieve(
        self,
        query_vector: List[float],
    ) -> List[Tuple[int, float]]:
        embeddings = self._fetch_embeddings()
        if not embeddings:
            return []

        if self.index.ntotal == 0:
            embeddings_matrix = self._deserialize_embeddings(embeddings)

            assert (
                embeddings_matrix.shape[1] == self.embedding_dim
            ), f"The dimension of the fetched embeddings ({embeddings_matrix.shape[1]}) does not match the FAISS index dimension ({self.embedding_dim})."

            self.index.add(embeddings_matrix)

        query_vector_array = np.array(query_vector).reshape(1, -1)
        distances, indices = self.index.search(
            query_vector_array, min(self.top_n, len(embeddings))
        )

        similarity_scores = np.exp(-self.lambda_param * distances[0])

        return [
            (embeddings[idx].id, similarity_scores[i])
            for i, idx in enumerate(indices[0])
        ]

    def get_params(self) -> Dict:
        return {
            "top_n": self.top_n,
            "embedding_dim": self.embedding_dim,
            "lambda_param": self.lambda_param,
        }

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
