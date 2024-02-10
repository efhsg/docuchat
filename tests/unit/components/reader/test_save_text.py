import unittest
from unittest.mock import patch

from components.reader.save_text import (
    file_already_exists,
    get_filenames_extracted_text,
    save_extracted_text,
    delete_extracted_text_dict,
)


class TestFileAlreadyExists(unittest.TestCase):
    @patch("components.reader.save_text.DatabaseManager")
    def test_file_already_exists(self, mock_db_manager):
        # Create an instance of the mock DatabaseManager
        mock_db_instance = mock_db_manager.return_value

        # Set up the mock name_exists method to return True for an existing file name
        mock_db_instance.name_exists.return_value = True
        # Assert that file_already_exists returns True for a file that exists
        self.assertTrue(file_already_exists("existing_file.txt"))
        # Verify name_exists was called with the correct file name
        mock_db_instance.name_exists.assert_called_once_with("existing_file.txt")

        # Reset mock to test for a file name that does not exist
        mock_db_instance.name_exists.return_value = False
        mock_db_instance.name_exists.reset_mock()

        # Assert that file_already_exists returns False for a file that does not exist
        self.assertFalse(file_already_exists("nonexistent_file.txt"))
        # Verify name_exists was called again with the new file name
        mock_db_instance.name_exists.assert_called_once_with("nonexistent_file.txt")


class TestGetFilenamesExtractedText(unittest.TestCase):
    @patch("components.reader.save_text.DatabaseManager")
    def test_get_filenames_extracted_text(self, mock_db_manager):
        # Prepare the mock response for get_names_of_extracted_texts
        expected_filenames = ["file1.txt", "file2.txt", "file3.txt"]
        mock_db_manager_instance = mock_db_manager.return_value
        mock_db_manager_instance.get_names_of_extracted_texts.return_value = (
            expected_filenames
        )

        # Call the function under test
        filenames = get_filenames_extracted_text()

        # Verify the result
        self.assertEqual(filenames, expected_filenames)
        # Check that get_names_of_extracted_texts was called as expected
        mock_db_manager_instance.get_names_of_extracted_texts.assert_called_once()

    @patch("components.reader.save_text.DatabaseManager")
    def test_save_extracted_text(self, mock_db_manager):
        # Create an instance of the mock DatabaseManager
        mock_db_instance = mock_db_manager.return_value

        # Dummy text and filename to be saved
        test_text = "This is a test text."
        test_filename = "test_file.txt"

        # Call the function under test
        save_extracted_text(test_text, test_filename)

        # Verify save_extracted_text_to_db was called with the correct arguments
        mock_db_instance.save_extracted_text_to_db.assert_called_once_with(
            test_text, test_filename
        )


class TestDeleteExtractedTextDict(unittest.TestCase):
    @patch("components.reader.save_text.DatabaseManager")
    def test_delete_extracted_text_dict(self, mock_db_manager):
        # Create an instance of the mock DatabaseManager
        mock_db_instance = mock_db_manager.return_value

        # Prepare a mock file dictionary with some files marked for deletion
        file_dict = {
            "file1.txt": True,  # Marked for deletion
            "file2.txt": False,  # Not marked for deletion
            "file3.txt": True,  # Marked for deletion
        }

        # Expected list of filenames to delete based on the file_dict
        expected_filenames_to_delete = ["file1.txt", "file3.txt"]

        # Call the function under test
        delete_extracted_text_dict(file_dict)

        # Verify delete_extracted_texts_bulk was called with the correct filenames
        mock_db_instance.delete_extracted_texts_bulk.assert_called_once_with(
            expected_filenames_to_delete
        )


if __name__ == "__main__":
    unittest.main()
