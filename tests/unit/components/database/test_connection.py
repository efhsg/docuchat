import unittest
from unittest.mock import patch, MagicMock
import pymysql
from sqlalchemy.exc import SQLAlchemyError
from components.database.mysql_connector import MySQLConnector


class TestConnection(unittest.TestCase):
    @patch("os.getenv")
    def test_get_connection_success(self, mock_getenv):
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
            connection_instance = MySQLConnector()
            connection_instance.get_connection()
            mock_connect.assert_called_once_with(
                host="localhost",
                user="user",
                password="password",
                database="test_db",
                port=3306,
                cursorclass=pymysql.cursors.DictCursor,
            )

    @patch("os.getenv")
    @patch("components.database.mysql_connector.NativeLogger.get_logger")
    def test_get_connection_failure(self, mock_get_logger, mock_getenv):
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
            connection_instance = MySQLConnector()
            with self.assertRaises(pymysql.Error):
                connection_instance.get_connection()
            mock_logger.critical.assert_called_once()

    @patch("components.database.mysql_connector.os.getenv")
    @patch("components.database.mysql_connector.create_engine")
    @patch("components.database.mysql_connector.sessionmaker", autospec=True)
    def test_create_session_success(
        self, mock_sessionmaker, mock_create_engine, mock_getenv
    ):
        mock_getenv.side_effect = lambda x, default=None: {
            "DB_HOST_DOCKER": "localhost",
            "RUNNING_IN_DOCKER": "false",
            "DB_HOST_VENV": "localhost",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_DATABASE": "test_db",
            "DB_PORT": "3306",
        }.get(x, default)

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        session_factory = mock_sessionmaker.return_value
        session = MagicMock()
        session_factory.return_value = session

        connection_instance = MySQLConnector()
        created_session = connection_instance.get_session()
        expected_uri = f"mysql+pymysql://user:password@localhost:3306/test_db"
        mock_create_engine.assert_called_once_with(expected_uri)
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        self.assertIsNotNone(created_session)

    @patch("components.database.mysql_connector.os.getenv")
    @patch("components.database.mysql_connector.create_engine")
    @patch("components.database.mysql_connector.sessionmaker", autospec=True)
    def test_create_session_failure(
        self, mock_sessionmaker, mock_create_engine, mock_getenv
    ):
        mock_getenv.side_effect = lambda x, default=None: {
            "DB_HOST_DOCKER": "localhost",
            "RUNNING_IN_DOCKER": "false",
            "DB_HOST_VENV": "localhost",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_DATABASE": "test_db",
            "DB_PORT": "3306",
        }.get(x, default)

        mock_create_engine.side_effect = SQLAlchemyError("Engine creation failed")

        connection_instance = MySQLConnector()

        with self.assertRaises(SQLAlchemyError) as context:
            connection_instance.get_session()

        self.assertEqual(str(context.exception), "Engine creation failed")
        mock_create_engine.assert_called_once_with(
            f"mysql+pymysql://user:password@localhost:3306/test_db"
        )
        mock_sessionmaker.assert_not_called()


if __name__ == "__main__":
    unittest.main()
