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
    def get_chunk_by_embedding_id_with_filename(
        self, id: int
    ) -> Tuple[Chunk, ExtractedText]: ...
