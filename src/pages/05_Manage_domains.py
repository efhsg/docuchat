import unittest
from unittest.mock import MagicMock, patch
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.database.models import Domain
from components.reader.interfaces.text_compressor import TextCompressor
from components.database.interfaces.connector import Connector
from logging import Logger


class TestSqlalchemyReaderRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock(spec=Connector)
        self.mock_connector.get_session.return_value = MagicMock()
        self.mock_logger = MagicMock(spec=Logger)
        self.mock_compressor = MagicMock(spec=TextCompressor)
        self.reader_repository = SqlalchemyReaderRepository(
            connector=self.mock_connector,
            compressor=self.mock_compressor,
            logger=self.mock_logger,
        )

    def test_create_domain_success(self):
        domain_name = "test_domain"
        self.reader_repository.create_domain(domain_name)
        self.mock_connector.get_session.return_value.add.assert_called()
        self.mock_connector.get_session.return_value.commit.assert_called()

    def test_create_domain_with_default_name_failure(self):
        with self.assertRaises(ValueError):
            self.reader_repository.create_domain("")

    def test_list_domains(self):
        self.mock_connector.get_session.return_value.query.return_value.all.return_value = [
            ("domain1",),
            ("domain2",),
        ]
        result = self.reader_repository.list_domains()
        self.assertEqual(result, ["domain1", "domain2"])

    def test_delete_domain_success(self):
        domain_name = "test_domain"
        self.reader_repository.delete_domain(domain_name)
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.delete.assert_called()
        self.mock_connector.get_session.return_value.commit.assert_called()

    def test_delete_texts_bulk_success(self):
        domain_name = "test_domain"
        texts = [("name1", "type1"), ("name2", "type2")]
        self.reader_repository.delete_texts(domain_name, texts)
        self.mock_connector.get_session.return_value.commit.assert_called()

    def test_get_text_by_name_found(self):
        domain_name = "test_domain"
        text_name = "dummy name"
        text_type = "type"
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock()
        )
        result = self.reader_repository.get_text_by_name(
            domain_name, text_name, text_type
        )
        self.assertIsNotNone(result)

    def test_move_text_success(self):
        source_domain = "source_domain"
        target_domain = "target_domain"
        texts = [("text1", "type")]
        self.reader_repository.move_text(source_domain, target_domain, texts)
        self.mock_connector.get_session.return_value.commit.assert_called()

    def test_save_text_success(self):
        domain_name = "test_domain"
        text_name = "dummy text"
        text_type = "type"
        original_name = "original name"
        text = "text"
        self.reader_repository.save_text(
            domain_name, text_name, text_type, original_name, text
        )
        self.mock_connector.get_session.return_value.add.assert_called()
        self.mock_connector.get_session.return_value.commit.assert_called()

    def test_text_exists_found(self):
        domain_name = "test_domain"
        text_name = "existing name"
        text_type = "type"
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock()
        )
        result = self.reader_repository.text_exists(domain_name, text_name, text_type)
        self.assertTrue(result)

    def test_text_exists_not_found(self):
        domain_name = "test_domain"
        text_name = "non-existing name"
        text_type = "type"
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            None
        )
        result = self.reader_repository.text_exists(domain_name, text_name, text_type)
        self.assertFalse(result)

    def test_update_domain_success(self):
        old_domain = "old_domain"
        new_domain = "new_domain"
        self.reader_repository.update_domain(old_domain, new_domain)
        self.mock_connector.get_session.return_value.commit.assert_called()


if __name__ == "__main__":
    unittest.main()
