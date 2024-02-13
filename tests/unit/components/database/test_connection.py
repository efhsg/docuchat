import unittest
from unittest.mock import patch, MagicMock

import pymysql
from components.database.connection import Connection


class TestConnection(unittest.TestCase):
    @patch("components.database.connection.Config")
    @patch("pymysql.connect")
    def test_create_connection_success(self, mock_connect, mock_config):
        mock_config_instance = mock_config.return_value
        mock_config_instance.db_host = "localhost"
        mock_config_instance.db_user = "user"
        mock_config_instance.db_password = "password"
        mock_config_instance.db_name = "test_db"

        connection_instance = Connection(mock_config_instance)
        connection = connection_instance.create_connection()

        mock_connect.assert_called_once_with(
            host="localhost",
            user="user",
            password="password",
            database="test_db",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.assertIsNotNone(connection)
