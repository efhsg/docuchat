import unittest
from unittest.mock import patch, MagicMock

from components.reader.text_repository import TextRepository
from components.database.models import ExtractedText


class TestTextRepository(unittest.TestCase):

    @patch("components.reader.db_reader.DBReader")
    def setUp(self, mock_DBReader):
        self.mock_DBReader = mock_DBReader.return_value
        self.text_repository = TextRepository(db_reader=self.mock_DBReader)
        self.mock_DBReader.compression_service.compress = MagicMock()
        self.mock_DBReader.compression_service.decompress = MagicMock()

    def test_save_text_with_domain(self):
        self.mock_DBReader.session.query.return_value.filter_by.return_value.first.return_value = (
            True
        )
        self.mock_DBReader.compression_service.compress.return_value = (
            b"compressed text"
        )

        try:
            self.text_repository.save_text("text", "name.txt", domain_id=1)
        except Exception as e:
            self.fail(f"save_text with domain_id raised an exception {e}")
        self.mock_DBReader.session.add.assert_called()
        self.mock_DBReader.session.commit.assert_called()

    def test_text_exists_true(self):
        self.mock_DBReader.name_exists.return_value = True
        exists = self.text_repository.text_exists("existing_file.txt")
        self.assertTrue(exists, "The text should exist.")
        self.mock_DBReader.name_exists.assert_called_once_with("existing_file.txt")

    def test_text_exists_false(self):
        self.mock_DBReader.name_exists.return_value = False
        exists = self.text_repository.text_exists("non_existing_file.txt")
        self.assertFalse(exists, "The text should not exist.")
        self.mock_DBReader.name_exists.assert_called_once_with("non_existing_file.txt")

    def test_list_text_names(self):
        expected_names = ["file1.txt", "file2.txt"]
        self.mock_DBReader.get_names_of_extracted_texts.return_value = expected_names

        names = self.text_repository.list_text_names()
        self.assertEqual(names, expected_names)
        self.mock_DBReader.get_names_of_extracted_texts.assert_called_once()

    def test_delete_texts(self):
        names_to_delete = ["file1.txt", "file3.txt"]
        self.text_repository.delete_texts(names_to_delete)
        self.mock_DBReader.delete_extracted_texts_bulk.assert_called_once_with(
            names_to_delete
        )


if __name__ == "__main__":
    unittest.main()
