import pymysql

from config import Config
from components.database.connection import Connection
from components.database.text_compression import TextCompression
from components.logger.logger import Logger


class ExtractText:

    logger = Logger.get_logger()

    def __init__(self, config=None, connection=None, compression_service=None):
        self.config = config or Config()
        self.connection = connection or Connection().create_connection()
        self.compression_service = compression_service or TextCompression()

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
