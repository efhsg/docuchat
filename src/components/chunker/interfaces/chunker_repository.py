from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from components.database.models import (
    Chunk,
    ChunkProcess,
    ExtractedText,
)


class ChunkerRepository(ABC):

    @abstractmethod
    def create_chunk_process(
        self, extracted_text_id: int, method: str, parameters: dict
    ) -> int:
        pass

    @abstractmethod
    def save_chunks(
        self, chunk_process_id: int, chunks: List[Tuple[int, bytes]]
    ) -> None:
        pass

    @abstractmethod
    def list_chunk_processes_by_text(
        self, extracted_text_id: int
    ) -> List[ChunkProcess]:
        pass

    @abstractmethod
    def list_chunks_by_process(self, chunk_process_id: int) -> List[Chunk]:
        pass

    @abstractmethod
    def get_chunk_process(
        self, extracted_text_id: int, method: str
    ) -> Optional[ChunkProcess]:
        pass

    @abstractmethod
    def delete_chunk_process(self, chunk_process_id: int) -> None:
        pass

    @abstractmethod
    def delete_chunks_by_process(self, chunk_process_id: int) -> None:
        pass

    @abstractmethod
    def update_chunk_process(self, chunk_process: ChunkProcess) -> None:
        pass

    @abstractmethod
    def list_unchunked_texts_by_domain(self, domain_name: str) -> List[ExtractedText]:
        pass

    @abstractmethod
    def list_chunked_texts_by_domain(self, domain_name: str) -> List[ExtractedText]:
        pass
