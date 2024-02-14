import os
from dotenv import load_dotenv
import pymysql
from pathlib import Path
from components.logger.logger import Logger
from config import Config


class Connection:
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

    def _load_env(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        dotenv_path = project_root / ".env"
        load_dotenv(dotenv_path)

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

    @property
    def database_url(self):
        return f"mysql+pymysql://{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}"
