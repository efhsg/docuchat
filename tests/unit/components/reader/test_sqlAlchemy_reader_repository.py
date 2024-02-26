import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from components.reader.sqlAlchemy_reader_repository import SqlalchemyReaderRepository
from components.reader.zlib_text_compressor import ZlibTextCompressor
from logging import Logger as StandardLogger


class TestSqlalchemyReaderRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock()
        self.mock_connector.get_session.return_value = MagicMock()
        self.mock_logger = MagicMock(spec=StandardLogger)
        self.mock_compressor = MagicMock(spec=ZlibTextCompressor)
        self.reader_repository = SqlalchemyReaderRepository(
            connector=self.mock_connector,
            compressor=self.mock_compressor,
            logger=self.mock_logger,
        )
        self.default_domain_name = "default"

    def test_create_domain_success(self):
        self.reader_repository.domain_exists = MagicMock(return_value=False)
        self.reader_repository.create_domain("test_domain")
        session = self.mock_connector.get_session.return_value
        session.add.assert_called_once()
        session.commit.assert_called_once()

    def test_create_domain_with_default_name_failure(self):
        with self.assertRaises(ValueError):
            self.reader_repository.create_domain(self.default_domain_name)

    def test_list_domains(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.all.return_value = [("domain1",), ("domain2",)]
        result = self.reader_repository.list_domains()
        self.assertEqual(result, ["domain1", "domain2"])

    def test_delete_domain_success(self):
        self.reader_repository.delete_domain("test_domain")
        session = self.mock_connector.get_session.return_value
        session.query.assert_called_once()

    def test_update_domain_success(self):
        session = self.mock_connector.get_session.return_value
        domain_mock = MagicMock()
        session.query.return_value.filter_by.return_value.first.side_effect = [
            domain_mock,
            None,
        ]

        self.reader_repository.domain_exists = MagicMock(return_value=False)

        try:
            self.reader_repository.update_domain("existing_domain", "new_unique_domain")
            update_success = True
        except ValueError:
            update_success = False

        self.assertTrue(
            update_success, "Domain update should succeed without raising ValueError"
        )

        self.assertEqual(
            domain_mock.name,
            "new_unique_domain",
            "Domain name should be updated to 'new_unique_domain'",
        )
        session.commit.assert_called_once()

    def test_update_default_domain_failure(self):
        with self.assertRaises(ValueError):
            self.reader_repository.update_domain(self.default_domain_name, "new_name")

    def test_delete_texts_bulk_success(self):
        self.reader_repository.delete_texts(
            self.default_domain_name,
            [("name1", "ext1")],
        )
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter.return_value.delete.assert_called_once()

    def test_list_text_names_by_domain_exception(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.one.side_effect = Exception(
            "Unexpected error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.list_text_names_by_domain("domain_with_error")

    def test_get_domain_id_found(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock(id=1)
        )
        domain_id = self.reader_repository._get_domain_id("existing_domain")
        self.assertEqual(domain_id, 1)

    def test_get_domain_id_not_found(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.first.return_value = None
        with self.assertRaises(ValueError):
            self.reader_repository._get_domain_id("non_existing_domain")

    def test_create_domain_failure_due_to_existing_domain(self):
        self.reader_repository.domain_exists = MagicMock(return_value=True)
        with self.assertRaises(ValueError):
            self.reader_repository.create_domain("existing_domain")

    def test_list_domains_with_exception(self):
        self.mock_connector.get_session.return_value.query.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.list_domains()

    def test_list_domains_with_extracted_texts_success(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.join.return_value.group_by.return_value.having.return_value.all.return_value = [
            ("domain_with_text",)
        ]
        result = self.reader_repository.list_domains_with_extracted_texts()
        self.assertEqual(result, ["domain_with_text"])

    def test_list_domains_with_extracted_texts_with_exception(self):
        self.mock_connector.get_session.return_value.query.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.list_domains_with_extracted_texts()

    def test_delete_domain_with_associated_texts_failure(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.delete.side_effect = IntegrityError(
            "Cannot delete", "param", "orig"
        )
        with self.assertRaises(ValueError):
            self.reader_repository.delete_domain("domain_with_texts")

    def test_delete_domain_with_exception(self):
        self.mock_connector.get_session.return_value.query.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(ValueError):
            self.reader_repository.delete_domain("error_domain")

    def test_update_domain_failure_due_to_existing_new_name(self):
        self.reader_repository.domain_exists = MagicMock(return_value=True)
        with self.assertRaises(ValueError):
            self.reader_repository.update_domain("old_name", "existing_new_name")

    def test_update_domain_with_nonexistent_old_name_failure(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            None
        )
        with self.assertRaises(ValueError):
            self.reader_repository.update_domain("nonexistent_old_name", "new_name")

    def test_update_domain_with_exception(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.side_effect = Exception(
            "DB error"
        )
        self.reader_repository.domain_exists = MagicMock(
            side_effect=Exception("DB error")
        )
        with self.assertRaises(Exception):
            self.reader_repository.update_domain("old_name", "new_name")

    def test_domain_exists_when_domain_does_not_exist(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            None
        )
        result = self.reader_repository.domain_exists("nonexistent_domain")
        self.assertFalse(result)

    def test_save_text_with_exception(self):
        self.mock_connector.get_session.return_value.add.side_effect = Exception(
            "DB error"
        )
        try:
            self.reader_repository.save_text("text", "name", "domain_name")
            self.fail("Exception was expected but not raised.")
        except Exception as e:
            self.assertIsInstance(e, Exception)

    def test_get_text_by_name_with_exception(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.get_text_by_name("text_name", "domain_name")

    def test_delete_texts_with_exception(self):
        self.mock_connector.get_session.return_value.query.return_value.filter.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.delete_texts(["name1", "name2"], "domain_name")

    def test_move_text_with_exception(self):
        self.reader_repository._get_domain_id = MagicMock(
            side_effect=Exception("DB error")
        )
        with self.assertRaises(Exception):
            self.reader_repository.move_text(
                "source_domain", "target_domain", ["text1"]
            )

    def test_update_text_name_with_exception(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.one.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.update_text_name(
                "old_name", "new_name", "domain_name"
            )
