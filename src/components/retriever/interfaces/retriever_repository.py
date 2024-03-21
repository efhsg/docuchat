from abc import ABC, abstractmethod
from components.database.models import (
    Chunk,
    Domain,
    ExtractedText,
)
from typing import List, Tuple


class RetrieverRepository(ABC):

    @abstractmethod
    def list_domains_with_embeddings(self) -> List[Domain]: ...

    @abstractmethod
    def get_chunk_by_embedding_id_with_text(
        self, id: int
    ) -> Tuple[Chunk, ExtractedText]: ...

    @abstractmethod
    def list_texts_by_domain_and_embedder(
        self, domain_name: str, embedder: str
    ) -> List[ExtractedText]: ...

    @abstractmethod
    def get_chunks_by_embedding_ids_with_texts(
        self, ids: List[int]
    ) -> List[Tuple[Chunk, ExtractedText]]: ...
