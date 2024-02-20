from components.database.mysql_connector import MySQLConnector
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor
from components.logger.native_logger import NativeLogger


def get_logger(name: str = "docuchat"):
    return NativeLogger.get_logger(name)


def get_reader_repository() -> ReaderRepository:
    return SqlalchemyReaderRepository(
        connector=MySQLConnector(),
        compressor=ZlibTextCompressor(),
        logger=NativeLogger.get_logger("docuchat"),
    )


def get_text_extractor() -> TextExtractor:
    return FileTextExtractor()
