import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from components.database.db_extract_text import ExtractText
from components.database.models import ExtractedText
from components.database.connection import Connection
from components.database.text_compression import TextCompression


class TestExtractText(unittest.TestCase):

    @patch("components.database.connection.Connection.create_session")
    @patch("components.database.text_compression.TextCompression.compress")
    def test_save_extracted_text_to_db_success(
        self, mock_compress, mock_create_session
    ):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_compress.return_value = b"compressed text"

        extract_text_instance = ExtractText(
            session=mock_session, compression_service=TextCompression()
        )
        extract_text_instance.save_extracted_text_to_db("dummy text", "dummy name")

        mock_compress.assert_called_once_with("dummy text")
        mock_session.add.assert_called_once()
        assert mock_session.commit.called

    @patch("components.database.connection.Connection.create_session")
    @patch("components.database.text_compression.TextCompression.compress")
    def test_save_extracted_text_to_db_failure(
        self, mock_compress, mock_create_session
    ):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_compress.return_value = b"compressed text"
        mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

        extract_text_instance = ExtractText(
            session=mock_session, compression_service=TextCompression()
        )

        with self.assertRaises(SQLAlchemyError):
            extract_text_instance.save_extracted_text_to_db("dummy text", "dummy name")

        mock_compress.assert_called_once_with("dummy text")
        mock_session.add.assert_called_once()
        assert mock_session.rollback.called

    @patch("components.database.connection.Connection.create_session")
    @patch("components.database.text_compression.TextCompression.decompress")
    def test_get_text_by_name_found(self, mock_decompress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_one = mock_filter_by.one.return_value
        mock_one.text = b"compressed text"
        mock_decompress.return_value = "decompressed text"

        extract_text_instance = ExtractText(
            session=mock_session, compression_service=TextCompression()
        )
        result = extract_text_instance.get_text_by_name("dummy name")

        mock_decompress.assert_called_once_with(b"compressed text")
        self.assertEqual(result, "decompressed text")

    @patch("components.database.connection.Connection.create_session")
    @patch("components.database.text_compression.TextCompression.decompress")
    def test_get_text_by_name_not_found(self, mock_decompress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.one.side_effect = NoResultFound

        extract_text_instance = ExtractText(
            session=mock_session, compression_service=TextCompression()
        )
        result = extract_text_instance.get_text_by_name("dummy name")

        mock_decompress.assert_not_called()
        self.assertIsNone(result)

    @patch("components.database.connection.Connection.create_session")
    def test_get_names_of_extracted_texts(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_query.all.return_value = [("name1",), ("name2",)]

        extract_text_instance = ExtractText(session=mock_session)
        result = extract_text_instance.get_names_of_extracted_texts()

        mock_session.query.assert_called_once_with(ExtractedText.name)
        self.assertEqual(result, ["name1", "name2"])

    @patch("components.database.connection.Connection.create_session")
    def test_name_exists_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.first.return_value = MagicMock(id=1)

        extract_text_instance = ExtractText(session=mock_session)
        result = extract_text_instance.name_exists("existing name")

        self.assertTrue(result)

    @patch("components.database.connection.Connection.create_session")
    def test_name_exists_not_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.first.return_value = None

        extract_text_instance = ExtractText(session=mock_session)
        result = extract_text_instance.name_exists("non-existing name")

        self.assertFalse(result)

    @patch("components.database.connection.Connection.create_session")
    def test_delete_extracted_texts_bulk_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session

        extract_text_instance = ExtractText(session=mock_session)
        extract_text_instance.delete_extracted_texts_bulk(["name1", "name2"])

        mock_session.query.assert_called_once_with(ExtractedText)
        assert mock_session.commit.called

    @patch("components.database.connection.Connection.create_session")
    def test_delete_extracted_texts_bulk_failure(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

        extract_text_instance = ExtractText(session=mock_session)

        with self.assertRaises(SQLAlchemyError):
            extract_text_instance.delete_extracted_texts_bulk(["name1", "name2"])

        assert mock_session.rollback.called

    @patch("components.database.connection.Connection.create_session")
    def test_delete_extracted_texts_bulk_empty_list(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session

        extract_text_instance = ExtractText(session=mock_session)
        extract_text_instance.delete_extracted_texts_bulk([])

        mock_session.query.assert_not_called()
        mock_session.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
