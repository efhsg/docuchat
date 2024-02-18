import os
from dotenv import load_dotenv

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from components.logger.logger import Logger
from config import Config


class Connector:
    def __init__(self):
        load_dotenv(Config().project_root / ".env")
        self._db_host = (
            os.getenv("DB_HOST_DOCKER")
            if os.getenv("RUNNING_IN_DOCKER", "false") == "true"
            else os.getenv("DB_HOST_VENV")
        )
        self._db_user = os.getenv("DB_USER")
        self._db_password = os.getenv("DB_PASSWORD")
        self._db_name = os.getenv("DB_DATABASE")
        self._db_port = os.getenv("DB_PORT", "3306")
        self.logger = Logger.get_logger()

    def create_connection(self):
        try:
            return pymysql.connect(
                host=self._db_host,
                user=self._db_user,
                password=self._db_password,
                database=self._db_name,
                port=int(self._db_port),
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.Error as e:
            error_message = f"Failed to connect to MySQL database: {e}"
            self.logger.critical(error_message)
            raise

    def create_session(self):
        try:
            engine = create_engine(self._database_uri())
            Session = sessionmaker(bind=engine)
            return Session()
        except Exception as e:
            self.logger.critical(f"Failed to create SQLAlchemy session: {e}")
            raise

    def _database_uri(self):
        return f"mysql+pymysql://{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}"
