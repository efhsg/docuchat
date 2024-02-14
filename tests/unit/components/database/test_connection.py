import unittest
from unittest.mock import patch
import pymysql
from components.database.connection import Connection


class TestConnection(unittest.TestCase):
    @patch("os.getenv")
    def test_create_connection_success(self, mock_getenv):
        mock_getenv.side_effect = lambda x, default=None: {
            "DB_HOST_DOCKER": "localhost",
            "RUNNING_IN_DOCKER": "false",
            "DB_HOST_VENV": "localhost",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_DATABASE": "test_db",
            "DB_PORT": "3306",
        }.get(x, default)
        with patch("pymysql.connect") as mock_connect:
            connection_instance = Connection()
            connection_instance.create_connection()
            mock_connect.assert_called_once_with(
                host="localhost",
                user="user",
                password="password",
                database="test_db",
                port=3306,
                cursorclass=pymysql.cursors.DictCursor,
            )

    @patch("os.getenv")
    @patch("components.database.connection.Logger.get_logger")
    def test_create_connection_failure(self, mock_get_logger, mock_getenv):
        mock_getenv.side_effect = lambda x, default=None: {
            "DB_HOST_DOCKER": "localhost",
            "RUNNING_IN_DOCKER": "false",
            "DB_HOST_VENV": "localhost",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_DATABASE": "test_db",
            "DB_PORT": "3306",
        }.get(x, default)
        mock_logger = mock_get_logger.return_value
        with patch("pymysql.connect") as mock_connect:
            mock_connect.side_effect = pymysql.Error("Connection failed")
            connection_instance = Connection()
            with self.assertRaises(pymysql.Error):
                connection_instance.create_connection()
            mock_logger.critical.assert_called_once()


if __name__ == "__main__":
    unittest.main()
