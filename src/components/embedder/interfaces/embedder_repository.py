from abc import ABC, abstractmethod
from components.database.models import (
    Chunk,
    ChunkProcess,
    Domain,
    Embedding,
    EmbeddingProcess,
    ExtractedText,
)
from typing import List, Tuple


class EmbedderRepository(ABC):

    @abstractmethod
    def list_domains_with_chunks(self) -> List[Domain]: ...

    @abstractmethod
    def list_extracted_texts_by_domain_with_chunks(
        self, domain_name: str
    ) -> List[ExtractedText]: ...

    @abstractmethod
    def list_chunk_processes_by_text(
        self, extracted_text_id: int
    ) -> List[ChunkProcess]: ...

    @abstractmethod
    def get_chunks_by_process_id(self, chunk_process_id: int) -> List[Chunk]: ...

    @abstractmethod
    def create_embedding_process(
        self, extracted_text_id: int, method: str, parameters: dict
    ) -> int: ...

    @abstractmethod
    def save_embedding(
        self, embedding_process_id: int, chunk_id: int, embedding: bytes
    ) -> None: ...

    @abstractmethod
    def list_embedding_processes_by_text(
        selected_text_d: int,
    ) -> List[EmbeddingProcess]: ...

    def list_embeddings_by_process(
        self, embedding_process: EmbeddingProcess
    ) -> List[Embedding]: ...

    @abstractmethod
    def update_embedding_process(self, embedding_process: EmbeddingProcess) -> None: ...

    @abstractmethod
    def delete_embeddings_by_process(self, embedding_process_id: int) -> None: ...

    @abstractmethod
    def delete_embedding_process(self, embedding_process_id: int) -> None: ...
