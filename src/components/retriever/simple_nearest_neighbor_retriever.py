from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from components.database.models import Chunk, ChunkProcess, Embedding, ExtractedText
from .interfaces.retriever import Retriever
import pickle
import base64
from logging import Logger as StandardLogger


class SimpleNearestNeighborRetriever(Retriever):
    def __init__(self, session: Session, logger: StandardLogger = None, top_n: int = 5):
        self.session = session
        self.logger = logger
        self.top_n = top_n

    def retrieve(
        self, domain_id: int, query_vector: List[float]
    ) -> List[Tuple[int, float]]:
        embeddings = (
            self.session.query(Embedding)
            .join(Chunk)
            .join(ChunkProcess)
            .join(ExtractedText)
            .filter(ExtractedText.domain_id == domain_id)
            .all()
        )
        embeddings_matrix = np.array(
            [pickle.loads(embedding.embedding) for embedding in embeddings]
        )
        query_vector_array = np.array(query_vector).reshape(1, -1)
        similarities = cosine_similarity(
            query_vector_array, embeddings_matrix
        ).flatten()
        top_indices = np.argsort(similarities)[-self.top_n :]

        return [(embeddings[i].id, similarities[i]) for i in top_indices]

    def get_configuration(self) -> dict:
        return {"method": "SimpleNearestNeighbor", "params": {"top_n": self.top_n}}
