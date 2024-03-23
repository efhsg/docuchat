import os
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .interfaces.connector import Connector
from components.logger.native_logger import NativeLogger
from config import Config


class MySQLConnector(Connector):
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
        self.logger = NativeLogger.get_logger()
        self._engine = None
        self._session_factory = None

    def get_connection(self):
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
            self.logger.critical(f"Failed to connect to MySQL database: {e}")
            raise

    def get_session(self):
        if not self._engine:
            self._engine = create_engine(self._database_uri())
        if not self._session_factory:
            self._session_factory = sessionmaker(bind=self._engine)
        return self._session_factory()

    def _database_uri(self):
        return f"mysql+pymysql://{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}"
