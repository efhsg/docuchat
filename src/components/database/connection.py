import pymysql
from config import Config
from components.logger.logger import Logger
from threading import Lock


class Connection:
    def __init__(self, config=None):
        self.config = config or Config()

    def create_connection(self):
        try:
            return pymysql.connect(
                host=self.config.db_host,
                user=self.config.db_user,
                password=self.config.db_password,
                database=self.config.db_name,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.Error as e:
            error_message = f"Failed to connect to MySQL database: {e}"
            self.logger.critical(error_message)
            raise
