import unittest
from unittest.mock import patch, MagicMock
from components.database.migration import Migration

from components.logger.logger import Logger

logger = Logger.get_logger()


class TestMigration(unittest.TestCase):
    @patch("components.database.mysql_connector.MySQLConnector.get_connection")
    @patch("components.database.migration.Logger.get_logger")
    def test_get_current_migration_version_success(
        self, mock_get_logger, mock_get_connection
    ):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"version_num": "abc123"}
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        migration = Migration()
        version = migration.get_current_migration_version()
        self.assertEqual(version, "abc123")

    @patch("components.database.mysql_connector.MySQLConnector.get_connection")
    @patch("components.database.migration.Logger.get_logger")
    def test_get_current_migration_version_none(
        self, mock_get_logger, mock_get_connection
    ):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        migration = Migration()
        version = migration.get_current_migration_version()
        self.assertIsNone(version)

    @patch("components.database.mysql_connector.MySQLConnector.get_connection")
    @patch("components.database.migration.Logger.get_logger")
    def test_get_current_migration_version_exception(
        self, mock_get_logger, mock_get_connection
    ):
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.side_effect = Exception(
            "Database error"
        )
        mock_get_connection.return_value = mock_connection
        mock_logger = mock_get_logger.return_value
        migration = Migration()
        version = migration.get_current_migration_version()
        self.assertIsNone(version)


if __name__ == "__main__":
    unittest.main()
