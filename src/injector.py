from components.database.interfaces.connector import Connector
from components.database.mysql_connector import MySQLConnector
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor
from components.logger.native_logger import NativeLogger
from sqlalchemy.orm import Session


def get_reader_repository() -> ReaderRepository:
    connector: Connector = MySQLConnector()
    logger = NativeLogger.get_logger("docuchat")
    return SqlalchemyReaderRepository(
        connector=connector, compressor=ZlibTextCompressor(), logger=logger
    )


def get_text_extractor() -> TextExtractor:
    return FileTextExtractor()
