from components.chunker.chunker_config import ChunkerConfig
from components.chunker.config_based_chunker_factory import ConfigBasedChunkerFactory
from components.chunker.interfaces.chunker_factory import ChunkerFactory
from components.chunker.interfaces.chunker_repository import ChunkerRepository
from components.chunker.sqlAlchemy_chunker_repository import SqlAlchemyChunkerRepository
from components.database.mysql_connector import MySQLConnector
from components.embedder.config_based_embedder_factory import ConfigBasedEmbedderFactory
from components.embedder.embedder_config import EmbedderConfig
from components.embedder.interfaces.embedder_factory import EmbedderFactory
from components.embedder.interfaces.embedder_repository import EmbedderRepository
from components.embedder.sqlAlchemy_embedder_repository import (
    SqlAlchemyEmbedderRepository,
)
from components.reader.interfaces.text_compressor import TextCompressor
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.web_text_extractor import WebTextExtractor
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor
from components.logger.native_logger import NativeLogger
from config import Config


def get_config() -> Config:
    return Config()


def get_logger(name: str = "docuchat"):
    return NativeLogger.get_logger(name)


def get_compressor() -> TextCompressor:
    return ZlibTextCompressor()


def get_reader_repository() -> ReaderRepository:
    return SqlalchemyReaderRepository(
        connector=MySQLConnector(),
        compressor=ZlibTextCompressor(),
        logger=NativeLogger.get_logger("docuchat"),
    )


def get_text_extractor() -> TextExtractor:
    return FileTextExtractor()


def get_web_extractor() -> TextExtractor:
    return WebTextExtractor(
        logger=NativeLogger.get_logger("docuchat"),
    )


def get_chunker_config():
    return ChunkerConfig()


def get_chunker_repository() -> ChunkerRepository:
    return SqlAlchemyChunkerRepository(
        connector=MySQLConnector(),
        compressor=ZlibTextCompressor(),
        logger=NativeLogger.get_logger("docuchat"),
    )


def get_embedder_repository() -> EmbedderRepository:
    return SqlAlchemyEmbedderRepository(
        connector=MySQLConnector(),
        compressor=ZlibTextCompressor(),
        logger=NativeLogger.get_logger("docuchat"),
    )


def get_chunker_factory() -> ChunkerFactory:
    return ConfigBasedChunkerFactory()


def get_embedder_config():
    return EmbedderConfig()


def get_embedder_factory() -> EmbedderFactory:
    return ConfigBasedEmbedderFactory()
