import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.database.models import ExtractedText
from components.reader.zlib_text_compressor import ZlibTextCompressor


class TestSqlalchemyReaderRepository(unittest.TestCase):

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    @patch("components.reader.zlib_text_compressor.ZlibTextCompressor.compress")
    def test_save_text_success(self, mock_compress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_compress.return_value = b"compressed text"
        reader_repository = SqlalchemyReaderRepository(
            session=mock_session, compressor=ZlibTextCompressor()
        )
        reader_repository.save_text("dummy text", "dummy name")
        mock_compress.assert_called_once_with("dummy text")
        mock_session.add.assert_called_once()
        self.assertTrue(mock_session.commit.called)

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    @patch("components.reader.zlib_text_compressor.ZlibTextCompressor.compress")
    def test_save_text_failure(self, mock_compress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_compress.return_value = b"compressed text"
        mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
        reader_repository = SqlalchemyReaderRepository(
            session=mock_session, compressor=ZlibTextCompressor()
        )
        with self.assertRaises(SQLAlchemyError):
            reader_repository.save_text("dummy text", "dummy name")
        mock_compress.assert_called_once_with("dummy text")
        mock_session.add.assert_called_once()
        self.assertTrue(mock_session.rollback.called)

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    @patch("components.reader.zlib_text_compressor.ZlibTextCompressor.decompress")
    def test_get_text_by_name_found(self, mock_decompress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_one = mock_filter_by.one.return_value
        mock_one.text = b"compressed text"
        mock_decompress.return_value = "decompressed text"
        reader_repository = SqlalchemyReaderRepository(
            session=mock_session, compressor=ZlibTextCompressor()
        )
        result = reader_repository.get_text_by_name("dummy name")
        mock_decompress.assert_called_once_with(b"compressed text")
        self.assertEqual(result, "decompressed text")

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_list_text_names(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_query.all.return_value = [("name1",), ("name2",)]
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.list_text_names()
        mock_session.query.assert_called_once_with(ExtractedText.name)
        self.assertEqual(result, ["name1", "name2"])

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_text_exists_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.first.return_value = MagicMock(id=1)
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.text_exists("existing name")
        self.assertTrue(result)

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_text_exists_not_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.first.return_value = None
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.text_exists("non-existing name")
        self.assertFalse(result)

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_delete_texts_bulk_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        reader_repository.delete_texts(["name1", "name2"])
        mock_session.query.assert_called_once_with(ExtractedText)
        assert mock_session.commit.called

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_delete_texts_bulk_failure(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        with self.assertRaises(SQLAlchemyError):
            reader_repository.delete_texts(["name1", "name2"])
        assert mock_session.rollback.called

    @patch("components.reader.sqlAlchemy_reader_repository.Connection.create_session")
    def test_delete_texts_bulk_empty_list(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        reader_repository.delete_texts([])
        mock_session.query.assert_not_called()
        mock_session.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
