from components.database.interfaces.connector import Connector
from components.database.mysql_connector import MySQLConnector
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor
from sqlalchemy.orm import Session


def get_session() -> Session:
    connector: Connector = MySQLConnector()
    return connector.get_session()


def get_reader_repository() -> ReaderRepository:
    session = get_session()
    return SqlalchemyReaderRepository(session=session, compressor=ZlibTextCompressor())


def get_text_extractor() -> TextExtractor:
    return FileTextExtractor()
