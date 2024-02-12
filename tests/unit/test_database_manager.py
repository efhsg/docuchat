import unittest
from unittest.mock import patch, MagicMock
from database_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    @patch("database_manager.pymysql.connect")  # Patch where connections are made
    def test_save_extracted_text_to_db(self, mock_connect):
        # Mocks with basic structure
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_config = MagicMock()
        mock_compression_service = MagicMock()

        # Configure your mocks
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_compression_service.compress.return_value = b"compressed_data"

        # Create DatabaseManager instance
        db_manager = DatabaseManager(
            config=mock_config,
            connection=mock_connection,
            compression_service=mock_compression_service,
        )

        # Test Data
        test_name = "unique_test_file.txt"
        test_text = "Unique test text content."

        # Execute the method
        db_manager.save_extracted_text_to_db(test_text, test_name)

        query = mock_cursor.execute.call_args[0][0].strip()
        expected_query = """
                INSERT INTO extracted_texts (name, text) VALUES (%s, %s)
                """.strip()
        assert query == expected_query

        mock_connection.commit.assert_called()

    @patch("database_manager.pymysql.connect")
    def test_get_text_by_name(self, mock_connect):
        # Mocks with basic structure
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_config = MagicMock()
        mock_compression_service = MagicMock()

        # Configure your mocks
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_compression_service.decompress.return_value = (
            "Decompressed test text content."
        )

        # Simulate database response
        mock_cursor.fetchone.return_value = {"text": b"compressed_data"}

        # Create DatabaseManager instance
        db_manager = DatabaseManager(
            config=mock_config,
            connection=mock_connection,
            compression_service=mock_compression_service,
        )

        # Test Data
        test_name = "unique_test_file.txt"

        # Execute the method
        result_text = db_manager.get_text_by_name(test_name)

        # Assert that the decompress method was called with the compressed data
        mock_compression_service.decompress.assert_called_with(b"compressed_data")

        # Assert the fetched text is as expected
        self.assertEqual(result_text, "Decompressed test text content.")

        # Assert the correct query was executed
        mock_cursor.execute.assert_called_with(
            "SELECT text FROM extracted_texts WHERE name = %s", (test_name,)
        )

    @patch("database_manager.pymysql.connect")
    def test_get_names_of_extracted_texts(self, mock_connect):
        # Mocks with basic structure
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_config = MagicMock()

        # Configure your mocks
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simulate database response with a list of names
        test_names = [
            {"name": "file1.txt"},
            {"name": "file2.txt"},
            {"name": "file3.txt"},
        ]
        mock_cursor.fetchall.return_value = test_names

        # Create DatabaseManager instance
        db_manager = DatabaseManager(config=mock_config, connection=mock_connection)

        # Execute the method
        result_names = db_manager.get_names_of_extracted_texts()

        # Assert the fetched names match the test data
        self.assertListEqual(result_names, [name["name"] for name in test_names])

        # Assert the correct query was executed
        mock_cursor.execute.assert_called_with("SELECT name FROM extracted_texts")

    @patch("database_manager.pymysql.connect")
    def test_name_exists(self, mock_connect):
        # Mocks with basic structure
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_config = MagicMock()

        # Configure your mocks
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Scenario 1: Name exists
        mock_cursor.fetchone.return_value = True  # Simulate finding an entry

        # Create DatabaseManager instance
        db_manager = DatabaseManager(config=mock_config, connection=mock_connection)

        # Test Data
        test_name_exists = "existing_file.txt"
        test_name_not_exists = "non_existing_file.txt"

        # Execute the method for a name that exists
        result_exists = db_manager.name_exists(test_name_exists)
        self.assertTrue(result_exists)

        # Adjust mock for a name that does not exist
        mock_cursor.fetchone.return_value = None  # Simulate not finding an entry

        # Execute the method for a name that does not exist
        result_not_exists = db_manager.name_exists(test_name_not_exists)
        self.assertFalse(result_not_exists)

        # Prepare expected calls with whitespace stripped
        expected_calls = [
            unittest.mock.call(
                """
                SELECT 1 FROM extracted_texts WHERE name = %s LIMIT 1
                """.strip(),
                (test_name_exists,),
            ),
            unittest.mock.call(
                """
                SELECT 1 FROM extracted_texts WHERE name = %s LIMIT 1
                """.strip(),
                (test_name_not_exists,),
            ),
        ]

        # Actual calls with whitespace stripped for comparison
        actual_calls = [
            unittest.mock.call(c.args[0].strip(), *c.args[1:])
            for c in mock_cursor.execute.call_args_list
        ]

        # Assert the correct query was executed for both checks
        self.assertEqual(expected_calls, actual_calls)

    @patch("database_manager.pymysql.connect")
    def test_delete_extracted_texts_bulk(self, mock_connect):
        # Mock setup
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_config = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # DatabaseManager instance
        db_manager = DatabaseManager(config=mock_config, connection=mock_connection)

        # Test data
        names_to_delete = ["file1.txt", "file2.txt", "file3.txt"]

        # Method execution
        db_manager.delete_extracted_texts_bulk(names_to_delete)

        # Expected SQL command and parameters
        placeholders = ", ".join(
            ["%s"] * len(names_to_delete)
        )  # Adapt number of placeholders
        expected_query = f"DELETE FROM extracted_texts WHERE name IN ({placeholders})"
        expected_params = names_to_delete  # Use list if your implementation does so

        # Assertion corrected for formatting and parameter structure
        actual_query, actual_params = mock_cursor.execute.call_args[0]
        self.assertEqual(actual_query.strip(), expected_query)
        self.assertEqual(actual_params, expected_params)

        # Verify commit
        mock_connection.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
