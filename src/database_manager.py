import pymysql
from config import Config
import zlib

from components.logger.logger import Logger


class DatabaseManager:

    logger = Logger.get_logger()

    def __init__(self, config=None, connection=None, compression_service=None):
        self.config = config or Config()
        self.connection = connection or self.create_connection()
        self.compression_service = compression_service or TextCompressionService()

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
            error_message = f"Failed to connect to MySQL database at '{self.config.db_host}' with user '{self.config.db_user}'. Error: {e}"
            self.logger.critical(error_message)
            raise pymysql.Error(error_message) from e

    def create_db_and_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS extracted_texts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                text LONGBLOB NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_bases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_base_texts (
                knowledge_base_id INT,
                extracted_text_id INT,
                PRIMARY KEY (knowledge_base_id, extracted_text_id),
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
                FOREIGN KEY (extracted_text_id) REFERENCES extracted_texts(id) ON DELETE CASCADE
                )
                """
            )
            self.connection.commit()

    def save_extracted_text_to_db(self, text, name):
        try:
            compressed_text = self.compression_service.compress(text)
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO extracted_texts (name, text) VALUES (%s, %s)
                    """,
                    (name, compressed_text),
                )
                self.connection.commit()
        except Exception as e:
            error_message = f"Failed to save '{name}'. Error: {e}"
            self.logger.critical(error_message)
            raise pymysql.Error(error_message) from e

    def get_text_by_name(self, name):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT text FROM extracted_texts WHERE name = %s", (name,))
            result = cursor.fetchone()
            if result:
                return self.compression_service.decompress(result["text"])
            else:
                return None

    def get_names_of_extracted_texts(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT name FROM extracted_texts")
            filenames = cursor.fetchall()
            return [filename["name"] for filename in filenames]

    def name_exists(self, name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM extracted_texts WHERE name = %s LIMIT 1
                """,
                (name,),
            )
            result = cursor.fetchone()
            return result is not None

    def delete_extracted_texts_bulk(self, names):
        if not names:
            return
        placeholders = ", ".join(
            ["%s"] * len(names)
        )  # Create placeholders for the query
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                DELETE FROM extracted_texts WHERE name IN ({placeholders})
                """,
                names,
            )
            self.connection.commit()


class TextCompressionService:
    def compress(self, text):
        return zlib.compress(text.encode("utf-8"))

    def decompress(self, compressed_text):
        return zlib.decompress(compressed_text).decode("utf-8")
