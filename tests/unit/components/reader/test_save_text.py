import unittest
from unittest.mock import patch, MagicMock

from components.reader.save_text import (
    file_already_exists,
    get_filenames_extracted_text,
    save_extracted_text,
    delete_extracted_text_dict,
)


class TestSaveText(unittest.TestCase):

    @patch("components.reader.save_text.ExtractText")
    def test_file_already_exists(self, mock_ExtractText):
        mock_instance = mock_ExtractText.return_value
        mock_instance.name_exists.return_value = True

        self.assertTrue(file_already_exists("existing_file.txt"))
        mock_instance.name_exists.assert_called_once_with("existing_file.txt")

    @patch("components.reader.save_text.ExtractText")
    def test_get_filenames_extracted_text(self, mock_ExtractText):
        mock_instance = mock_ExtractText.return_value
        mock_instance.get_names_of_extracted_texts.return_value = [
            "file1.txt",
            "file2.txt",
        ]

        filenames = get_filenames_extracted_text()
        self.assertEqual(filenames, ["file1.txt", "file2.txt"])
        mock_instance.get_names_of_extracted_texts.assert_called_once()

    @patch("components.reader.save_text.ExtractText")
    def test_save_extracted_text(self, mock_ExtractText):
        mock_instance = mock_ExtractText.return_value

        save_extracted_text("sample text", "new_file.txt")
        mock_instance.save_extracted_text.assert_called_once_with(
            "sample text", "new_file.txt"
        )

    @patch("components.reader.save_text.ExtractText")
    def test_delete_extracted_text_dict(self, mock_ExtractText):
        mock_instance = mock_ExtractText.return_value
        file_dict = {"file1.txt": True, "file2.txt": False, "file3.txt": True}

        delete_extracted_text_dict(file_dict)
        mock_instance.delete_extracted_texts_bulk.assert_called_once_with(
            ["file1.txt", "file3.txt"]
        )


if __name__ == "__main__":
    unittest.main()
