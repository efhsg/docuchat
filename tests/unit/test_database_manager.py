import sqlite3
import unittest
from database_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.db_manager = DatabaseManager(connection=cls.conn)
        cls.db_manager.create_db_and_table()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.conn.execute("DELETE FROM extracted_texts")
        test_data = [
            ("test_file_1.txt", "This is the first test."),
            ("test_file_2.txt", "This is the second test."),
            ("test_file_3.txt", "This is the third test."),
            ("test_file_4.txt", "This is the fourth test."),
        ]
        for name, text_content in test_data:
            self.db_manager.save_extracted_text_to_db(text_content, name)

    def test_create_db_and_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='extracted_texts'"
        )
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists)

    def test_save_extracted_text_to_db(self):
        test_name = "unique_test_file.txt"
        test_text = "Unique test text content."
        self.db_manager.save_extracted_text_to_db(test_text, test_name)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, text_content FROM extracted_texts WHERE name = ?",
            (test_name,),
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], test_name)
        self.assertEqual(result[1], test_text)

    def test_get_names_of_extracted_texts(self):
        expected_names = [
            "test_file_1.txt",
            "test_file_2.txt",
            "test_file_3.txt",
            "test_file_4.txt",
        ]
        actual_names = self.db_manager.get_names_of_extracted_texts()
        self.assertListEqual(sorted(actual_names), sorted(expected_names))

    def test_name_exists(self):
        self.assertTrue(self.db_manager.name_exists("test_file_1.txt"))
        self.assertTrue(self.db_manager.name_exists("test_file_2.txt"))
        self.assertFalse(self.db_manager.name_exists("nonexistent_file.txt"))

    def test_delete_extracted_texts_bulk(self):
        names_to_delete = ["test_file_1.txt", "test_file_3.txt"]
        self.db_manager.delete_extracted_texts_bulk(names_to_delete)
        for name in names_to_delete:
            self.assertFalse(self.db_manager.name_exists(name))
        self.assertTrue(self.db_manager.name_exists("test_file_2.txt"))
        self.assertTrue(self.db_manager.name_exists("test_file_4.txt"))


if __name__ == "__main__":
    unittest.main()
