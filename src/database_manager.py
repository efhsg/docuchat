import sqlite3
from config import Config


class DatabaseManager:
    def __init__(self):
        self.db_path = Config().db_path

    def create_db_and_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS extracted_texts (
                    id INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL,
                    text_content TEXT NOT NULL
                )
            """
            )

    def save_extracted_text_to_db(self, text, filename="extracted_text"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO extracted_texts (filename, text_content) VALUES (?, ?)
            """,
                (filename, text),
            )

    def get_filenames_of_extracted_texts(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM extracted_texts")
            filenames = cursor.fetchall()
            return [filename[0] for filename in filenames]

    def filename_exists(self, filename):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT EXISTS(SELECT 1 FROM extracted_texts WHERE filename = ?)
            """,
                (filename,),
            )
            exists = cursor.fetchone()[0]
            return bool(exists)

    def delete_extracted_texts_bulk(self, filenames):
        if not filenames:
            return
        placeholders = ",".join("?" for _ in filenames)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"""
                DELETE FROM extracted_texts WHERE filename IN ({placeholders})
            """,
                filenames,
            )
