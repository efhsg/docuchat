import base64
from typing import Dict, List
from sqlalchemy import exists
from sqlalchemy.exc import SQLAlchemyError


from components.database.interfaces.connector import Connector
from components.reader.interfaces.text_compressor import TextCompressor
from .interfaces.embedder_repository import EmbedderRepository
from components.database.models import (
    Chunk,
    ChunkProcess,
    Domain,
    Embedding,
    EmbeddingProcess,
    ExtractedText,
)
from logging import Logger as StandardLogger


class SqlAlchemyEmbedderRepository(EmbedderRepository):
    def __init__(
        self,
        connector: Connector = None,
        compressor: TextCompressor = None,
        logger: StandardLogger = None,
    ):
        self.session = connector.get_session()
        self.compressor = compressor
        self.logger = logger

    def list_domains_with_chunks(self) -> List[Domain]:
        return (
            self.session.query(Domain)
            .join(ExtractedText, Domain.id == ExtractedText.domain_id)
            .filter(exists().where(ChunkProcess.extracted_text_id == ExtractedText.id))
            .all()
        )

    def list_extracted_texts_by_domain_with_chunks(
        self, domain_name: str
    ) -> List[ExtractedText]:
        return (
            self.session.query(ExtractedText)
            .join(Domain, Domain.id == ExtractedText.domain_id)
            .filter(Domain.name == domain_name)
            .filter(exists().where(ChunkProcess.extracted_text_id == ExtractedText.id))
            .all()
        )

    def list_chunk_processes_by_text_id(self, extracted_text_id):
        return (
            self.session.query(ChunkProcess)
            .filter(ChunkProcess.extracted_text_id == extracted_text_id)
            .order_by(ChunkProcess.id.desc())
            .all()
        )

    def get_chunks_by_process_id(self, chunk_process_id: int) -> List[Chunk]:
        try:
            chunks = (
                self.session.query(Chunk)
                .filter(Chunk.chunk_process_id == chunk_process_id)
                .all()
            )
            return chunks
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to list chunks by process ID {chunk_process_id}: {e}"
            )
            raise

    def create_embedding_process(
        self, chunk_process_id: int, method: str, parameters: dict
    ) -> int:
        try:
            embedding_process = EmbeddingProcess(
                chunk_process_id=chunk_process_id,
                method=method,
                parameters=parameters,
            )
            self.session.add(embedding_process)
            self.session.commit()
            return embedding_process.id
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to create embedding process: {e}")
            raise

    def save_embedding(
        self, embedding_process_id: int, chunk_id: int, embedding: str
    ) -> None:
        try:
            existing_embedding = (
                self.session.query(Embedding)
                .filter(
                    Embedding.chunk_id == chunk_id,
                    Embedding.embedding_process_id == embedding_process_id,
                )
                .one_or_none()
            )

            embedding_bytes = base64.b64decode(embedding)

            if existing_embedding:
                existing_embedding.embedding = embedding_bytes
            else:
                new_embedding = Embedding(
                    embedding_process_id=embedding_process_id,
                    chunk_id=chunk_id,
                    embedding=embedding_bytes,
                )
                self.session.add(new_embedding)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to save embedding for chunk ID {chunk_id} in embedding process ID {embedding_process_id}: {e}"
            )
            raise

    def list_embedding_processes_by_chunk_process_id(
        self, chunk_process_id: int
    ) -> List[EmbeddingProcess]:
        try:
            embedding_processes = (
                self.session.query(EmbeddingProcess)
                .filter(EmbeddingProcess.chunk_process_id == chunk_process_id)
                .all()
            )
            return embedding_processes
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to list embedding processes by chunk process ID {chunk_process_id}: {e}"
            )
            raise

    def list_embeddings_by_process_id(
        self, embedding_process: EmbeddingProcess
    ) -> List[Embedding]:
        try:
            embeddings = (
                self.session.query(Embedding)
                .filter(Embedding.embedding_process_id == embedding_process.id)
                .all()
            )
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to list embeddings by process: {e}")
            raise

    def update_embedding_process(self, embedding_process: EmbeddingProcess) -> None:
        try:
            self.session.merge(embedding_process)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to update embedding process: {e}")
            raise

    def delete_embeddings_by_process_id(self, embedding_process_id: int) -> None:
        try:
            embeddings = self.session.query(Embedding).filter(
                Embedding.embedding_process_id == embedding_process_id
            )
            embeddings.delete(synchronize_session="fetch")
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to delete embeddings for process ID {embedding_process_id}: {e}"
            )
            raise

    def delete_embedding_process(self, embedding_process_id: int) -> None:
        try:
            embedding_process = (
                self.session.query(EmbeddingProcess)
                .filter(EmbeddingProcess.id == embedding_process_id)
                .one_or_none()
            )

            if embedding_process:
                self.session.delete(embedding_process)
                self.session.commit()
            else:
                self.logger.warning(
                    f"No embedding process found with ID {embedding_process_id}, nothing to delete."
                )
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to delete embedding process ID {embedding_process_id}: {e}"
            )
            raise
