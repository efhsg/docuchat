from typing import List

from components.database.models import ChunkProcess, Chunk, Domain, ExtractedText
from .interfaces.chunker_repository import ChunkerRepository
from components.reader.interfaces.text_compressor import TextCompressor
from components.database.interfaces.connector import Connector
from sqlalchemy.exc import SQLAlchemyError
from logging import Logger as StandardLogger
from sqlalchemy.orm.exc import NoResultFound


class SqlAlchemyChunkerRepository(ChunkerRepository):
    def __init__(
        self,
        config=None,
        connector: Connector = None,
        compressor: TextCompressor = None,
        logger: StandardLogger = None,
    ):
        self.config = config

        self.session = connector.get_session()
        self.compressor = compressor
        self.logger = logger

    def create_chunk_process(self, extracted_text_id, method, parameters):
        try:
            chunk_process = ChunkProcess(
                extracted_text_id=extracted_text_id,
                method=method,
                parameters=parameters,
            )
            self.session.add(chunk_process)
            self.session.commit()
            return chunk_process.id
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to create chunk process: {e}")
            raise

    def save_chunks(self, chunk_process_id, chunks):
        try:
            for index, chunk_data in chunks:
                chunk = Chunk(
                    chunk_process_id=chunk_process_id,
                    index=index,
                    chunk=self.compressor.compress(chunk_data),
                )
                self.session.add(chunk)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to save chunks: {e}")
            raise

    def list_chunk_processes_by_text(self, extracted_text_id):
        try:
            return (
                self.session.query(ChunkProcess)
                .filter(ChunkProcess.extracted_text_id == extracted_text_id)
                .order_by(ChunkProcess.id.desc())
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to list chunk processes by text: {e}")
            raise

    def list_chunks_by_process(self, chunk_process_id):
        try:
            return (
                self.session.query(Chunk)
                .filter(Chunk.chunk_process_id == chunk_process_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to list chunks by process: {e}")
            raise

    def get_chunk_process(self, extracted_text_id, method):
        try:
            return (
                self.session.query(ChunkProcess)
                .filter(
                    ChunkProcess.extracted_text_id == extracted_text_id,
                    ChunkProcess.method == method,
                )
                .first()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get chunk process: {e}")
            raise

    def delete_chunk_process(self, chunk_process_id):
        try:
            self.session.query(ChunkProcess).filter(
                ChunkProcess.id == chunk_process_id
            ).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to delete chunk process: {e}")
            raise

    def delete_chunks_by_process(self, chunk_process_id):
        try:
            self.session.query(Chunk).filter(
                Chunk.chunk_process_id == chunk_process_id
            ).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to delete chunks by process: {e}")
            raise

    def update_chunk_process(self, chunk_process: ChunkProcess) -> None:
        try:
            self.session.merge(chunk_process)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Failed to update chunk process: {e}")
            raise

    def list_unchunked_texts_by_domain(self, domain_name: str) -> List[ExtractedText]:
        try:
            domain = self.session.query(Domain).filter_by(name=domain_name).one()
            unchunked_texts = (
                self.session.query(ExtractedText)
                .outerjoin(
                    ChunkProcess, ExtractedText.id == ChunkProcess.extracted_text_id
                )
                .filter(ExtractedText.domain_id == domain.id, ChunkProcess.id == None)
                .order_by(ExtractedText.name)
                .all()
            )
            return unchunked_texts
        except NoResultFound:
            return []
        except Exception as e:
            self.logger.error(
                f"Failed to list unchunked texts for domain '{domain_name}'. Error: {e}"
            )
            raise

    def list_chunked_texts_by_domain(self, domain_name: str) -> List[ExtractedText]:
        try:
            domain = self.session.query(Domain).filter_by(name=domain_name).one()
            chunked_texts = (
                self.session.query(ExtractedText)
                .join(ChunkProcess, ExtractedText.id == ChunkProcess.extracted_text_id)
                .filter(ExtractedText.domain_id == domain.id)
                .distinct()
                .order_by(ExtractedText.name)
                .all()
            )
            return chunked_texts
        except NoResultFound:
            return []
        except Exception as e:
            self.logger.error(
                f"Failed to list chunked texts for domain '{domain_name}'. Error: {e}"
            )
            raise
