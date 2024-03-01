from components.chunker.chunker_config import ChunkerConfig
from components.chunker.interfaces.chunker_repository import ChunkerRepository
from components.chunker.sqlAlchemy_chunker_repository import SqlAlchemyChunkerRepository
from components.database.mysql_connector import MySQLConnector
from components.reader.interfaces.text_compressor import TextCompressor
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.web_text_extractor import WebTextExtractor
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor
from components.logger.native_logger import NativeLogger
from config import Config
from pages.utils.interfaces.form import Form
from pages.utils.streamlit_form import StreamlitForm


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


def get_form() -> Form:
    return StreamlitForm()


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
