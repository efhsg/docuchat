import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.database.models import Domain, ExtractedText
from components.reader.zlib_text_compressor import ZlibTextCompressor


class TestSqlalchemyReaderRepository(unittest.TestCase):

    @patch("injector.get_session")
    @patch(
        "components.reader.sqlAlchemy_reader_repository.SqlalchemyReaderRepository.domain_exists",
        return_value=False,
    )
    def test_create_domain_success(self, mock_domain_exists, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        reader_repository.create_domain("test_domain")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("injector.get_session")
    def test_create_domain_with_default_name_failure(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        default_domain_name = reader_repository.config.default_domain_name
        with self.assertRaises(ValueError):
            reader_repository.create_domain(default_domain_name)

    @patch("injector.get_session")
    def test_list_domains(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.query.return_value.all.return_value = [("domain1",), ("domain2",)]
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.list_domains()
        self.assertEqual(result, ["domain1", "domain2"])

    @patch("injector.get_session")
    def test_list_domains_without_default(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = [
            ("domain1",),
            ("domain2",),
        ]
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        domains = reader_repository.list_domains_without_default()
        self.assertNotIn(
            reader_repository.config.default_domain_name.lower(),
            [domain.lower() for domain in domains],
        )

    @patch("injector.get_session")
    def test_delete_domain_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        reader_repository.delete_domain("test_domain")
        mock_session.query.assert_called_once()

    @patch("injector.get_session")
    def test_update_domain_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        with self.assertRaises(ValueError):
            reader_repository.update_domain("default_domain", "new_name")

    @patch("injector.get_session")
    def test_update_default_domain_failure(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        default_domain_name = reader_repository.config.default_domain_name
        with self.assertRaises(ValueError):
            reader_repository.update_domain(default_domain_name, "new_name")

    @patch("injector.get_session")
    def test_delete_default_domain_failure(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        default_domain_name = reader_repository.config.default_domain_name
        with self.assertRaises(ValueError):
            reader_repository.delete_domain(default_domain_name)

    @patch("injector.get_session")
    def test_delete_texts_bulk_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        reader_repository.delete_texts(["name1", "name2"])
        mock_session.query.return_value.filter.return_value.delete.assert_called_once()

    @patch("injector.get_session")
    @patch("components.reader.zlib_text_compressor.ZlibTextCompressor.decompress")
    def test_get_text_by_name_found(self, mock_decompress, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_decompress.return_value = "decompressed text"
        mock_session.query.return_value.filter_by.return_value.one.return_value.text = (
            b"compressed text"
        )
        reader_repository = SqlalchemyReaderRepository(
            session=mock_session, compressor=ZlibTextCompressor()
        )
        result = reader_repository.get_text_by_name("dummy name")
        self.assertEqual(result, "decompressed text")

    @patch("injector.get_session")
    def test_list_text_names(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.list_text_names()
        self.assertIsInstance(result, list)

    @patch("injector.get_session")
    def test_save_text_success(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(
            session=mock_session, compressor=ZlibTextCompressor()
        )
        reader_repository.save_text("dummy text", "dummy name")
        mock_session.add.assert_called_once()

    @patch("injector.get_session")
    def test_text_exists_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.text_exists("existing name")
        self.assertTrue(result)

    @patch("injector.get_session")
    def test_text_exists_not_found(self, mock_create_session):
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        reader_repository = SqlalchemyReaderRepository(session=mock_session)
        result = reader_repository.text_exists("non-existing name")
        self.assertFalse(result)
