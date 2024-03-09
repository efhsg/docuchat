from typing import List, Tuple
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from components.database.interfaces.connector import Connector
from components.reader.interfaces.text_compressor import TextCompressor
from .interfaces.retriever_repository import RetrieverRepository
from components.database.models import (
    Chunk,
    ChunkProcess,
    Domain,
    Embedding,
    ExtractedText,
)
from logging import Logger as StandardLogger


class SqlAlchemyRetrieverRepository(RetrieverRepository):
    def __init__(
        self,
        connector: Connector = None,
        compressor: TextCompressor = None,
        logger: StandardLogger = None,
    ):
        self.session = connector.get_session()
        self.compressor = compressor
        self.logger = logger

    def list_domains_with_embeddings(self) -> List[Domain]:
        try:
            return (
                self.session.query(Domain)
                .join(ExtractedText, Domain.id == ExtractedText.domain_id)
                .join(ChunkProcess, ExtractedText.id == ChunkProcess.extracted_text_id)
                .join(Chunk, ChunkProcess.id == Chunk.chunk_process_id)
                .join(Embedding, Chunk.id == Embedding.chunk_id)
                .distinct()
                .all()
            )
        except SQLAlchemyError as e:
            if self.logger:
                self.logger.error(f"SQLAlchemy error occurred: {e}")
            raise

    def get_chunk_by_embedding_id_with_filename(
        self, id: int
    ) -> Tuple[Chunk, ExtractedText]:
        try:
            chunk_with_filename = (
                self.session.query(Chunk, ExtractedText)
                .join(ChunkProcess, Chunk.chunk_process_id == ChunkProcess.id)
                .join(ExtractedText, ChunkProcess.extracted_text_id == ExtractedText.id)
                .join(Embedding, Embedding.chunk_id == Chunk.id)
                .filter(Embedding.id == id)
                .one()
            )
            return chunk_with_filename
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to retrieve chunk and filename for embedding ID {id}: {e}"
            )
            raise

    def list_texts_by_domain(self, domain_name):
        try:
            domain = self.session.query(Domain).filter_by(name=domain_name).one()
            texts = (
                self.session.query(ExtractedText)
                .filter_by(domain_id=domain.id)
                .order_by(ExtractedText.name)
                .all()
            )
            return texts
        except NoResultFound:
            self.logger.error(f"Domain '{domain_name}' does not exist.")
            return []
        except Exception as e:
            self.logger.error(
                f"Failed to list texts for domain '{domain_name}'. Error: {e}"
            )
            raise

    def list_texts_by_domain_and_embedder(self, domain_name: str, embedder_model: str):
        try:
            all_texts = self.list_texts_by_domain(domain_name)
            filtered_texts = []

            for text in all_texts:
                for chunk_process in text.chunk_processes:
                    for embedding_process in chunk_process.embedding_processes:
                        if embedding_process.parameters.get("model") == embedder_model:
                            filtered_texts.append(text)
                            break

            return filtered_texts
        except NoResultFound:
            self.logger.error(f"Domain '{domain_name}' does not exist.")
            return []
        except Exception as e:
            self.logger.error(
                f"Failed to list texts for domain '{domain_name}'. Error: {e}"
            )
            raise
