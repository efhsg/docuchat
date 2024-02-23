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
        self.default_domain_name = self.reader_repository.config.default_domain_name

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

    def test_list_domains_without_default(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter.return_value.all.return_value = [
            ("domain1",),
            ("domain2",),
        ]
        domains = self.reader_repository.list_domains_without_default()
        self.assertNotIn(
            self.default_domain_name.lower(),
            [domain.lower() for domain in domains],
        )

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

    def test_delete_default_domain_failure(self):
        with self.assertRaises(ValueError):
            self.reader_repository.delete_domain(self.default_domain_name)

    def test_delete_texts_bulk_success(self):
        self.reader_repository.delete_texts(
            ["name1", "name2"], self.default_domain_name
        )
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter.return_value.delete.assert_called_once()

    def test_get_text_by_name_found(self):
        self.mock_compressor.decompress.return_value = "decompressed text"
        session = self.mock_connector.get_session.return_value
        mocked_query_result = MagicMock(text=b"compressed text")
        session.query.return_value.filter_by.return_value.one.return_value = (
            mocked_query_result
        )
        result = self.reader_repository.get_text_by_name(
            "dummy name", self.default_domain_name
        )
        self.assertEqual(result, "decompressed text")

    def test_list_text_names(self):
        result = self.reader_repository.list_text_names()
        self.assertIsInstance(result, list)

    def test_save_text_success(self):
        self.reader_repository.text_exists = MagicMock(return_value=False)
        self.reader_repository.save_text("dummy text", "dummy name", "dummy_domain")

        session = self.mock_connector.get_session.return_value
        session.add.assert_called_once()

    def test_text_exists_found(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock()
        )
        result = self.reader_repository.text_exists("existing name", "domain_name")
        self.assertTrue(result)

    def test_text_exists_not_found(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        with patch.object(self.reader_repository, "_get_domain_id", return_value=1):
            result = self.reader_repository.text_exists(
                "non-existing name", "domain_name"
            )
            self.assertFalse(result)

    def test_list_text_names_by_domain_success(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.one.return_value = MagicMock(
            id=1
        )
        session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [
            ("text1",),
            ("text2",),
        ]
        result = self.reader_repository.list_text_names_by_domain("domain1")
        self.assertEqual(result, ["text1", "text2"])

    def test_list_text_names_by_domain_no_result(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.one.side_effect = (
            NoResultFound
        )
        self.mock_logger.error = MagicMock()
        result = self.reader_repository.list_text_names_by_domain("non_existent_domain")
        self.assertEqual(result, [])
        self.mock_logger.error.assert_called_once()

    def test_list_text_names_by_domain_exception(self):
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter_by.return_value.one.side_effect = Exception(
            "Unexpected error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.list_text_names_by_domain("domain_with_error")

    def test_move_text_success(self):
        self.reader_repository._get_domain_id = MagicMock(side_effect=[1, 2])
        self.reader_repository.list_text_names_by_domain = MagicMock(return_value=[])
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter.return_value.all.return_value = [
            MagicMock(name="text1", domain_id=1),
        ]
        self.mock_logger.info = MagicMock()
        skipped_texts = self.reader_repository.move_text(
            "source_domain", "target_domain", ["text1"]
        )
        self.assertEqual(skipped_texts, [])
        self.mock_logger.info.assert_called()

    def test_move_text_source_target_same(self):
        self.mock_logger.error = MagicMock()
        with self.assertRaises(ValueError):
            self.reader_repository.move_text(
                "source_domain", "source_domain", ["text1"]
            )
        self.mock_logger.error.assert_called_once()

    def test_move_text_exception(self):
        self.reader_repository._get_domain_id = MagicMock(side_effect=[1, 2])
        self.reader_repository.list_text_names_by_domain = MagicMock(return_value=[])
        session = self.mock_connector.get_session.return_value
        session.query.return_value.filter.return_value.all.side_effect = Exception(
            "Unexpected error"
        )
        self.mock_logger.error = MagicMock()
        with self.assertRaises(ValueError):
            self.reader_repository.move_text(
                "source_domain", "target_domain", ["text1"]
            )
        self.mock_logger.error.assert_called_once()

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

    def test_list_domains_without_default_with_exception(self):
        self.mock_connector.get_session.return_value.query.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.list_domains_without_default()

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

    def test_save_text_failure_due_to_existing_text(self):
        self.reader_repository.text_exists = MagicMock(return_value=True)
        self.reader_repository.save_text("text", "existing_name", "domain_name")
        session = self.mock_connector.get_session.return_value
        session.add.assert_not_called()

    def test_save_text_with_exception(self):
        self.mock_connector.get_session.return_value.add.side_effect = Exception(
            "DB error"
        )
        try:
            self.reader_repository.save_text("text", "name", "domain_name")
            self.fail("Exception was expected but not raised.")
        except Exception as e:
            self.assertIsInstance(e, Exception)

    def test_get_text_by_name_not_found(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.side_effect = (
            NoResultFound()
        )
        result = self.reader_repository.get_text_by_name(
            "nonexistent_text", "domain_name"
        )
        self.assertIsNone(result)

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

    def test_update_text_name_failure_due_to_existing_new_name(self):
        self.reader_repository.text_exists = MagicMock(return_value=True)
        with self.assertRaises(ValueError):
            self.reader_repository.update_text_name(
                "old_name", "existing_new_name", "domain_name"
            )

    def test_update_text_name_with_nonexistent_old_name_failure(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.one.side_effect = (
            NoResultFound
        )
        with self.assertRaises(ValueError):
            self.reader_repository.update_text_name(
                "nonexistent_old_name", "new_name", "domain_name"
            )

    def test_update_text_name_with_exception(self):
        self.mock_connector.get_session.return_value.query.return_value.filter_by.return_value.one.side_effect = Exception(
            "DB error"
        )
        with self.assertRaises(Exception):
            self.reader_repository.update_text_name(
                "old_name", "new_name", "domain_name"
            )
