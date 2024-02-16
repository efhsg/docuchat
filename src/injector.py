from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.zlib_text_compressor import ZlibTextCompressor
from components.reader.interfaces.text_extractor import TextExtractor
from components.reader.file_text_extractor import FileTextExtractor


def get_reader_repository() -> ReaderRepository:
    return SqlalchemyReaderRepository(compressor=ZlibTextCompressor())


def get_text_extractor() -> TextExtractor:
    return FileTextExtractor()
