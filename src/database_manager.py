import sqlite3
from config import Config


class DatabaseManager:
    def __init__(self, connection=None):
        self.db_path = Config().db_path
        self.connection = connection if connection else sqlite3.connect(self.db_path)

    def create_db_and_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS extracted_texts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                text_content TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def save_extracted_text_to_db(self, text, name="extracted_text"):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO extracted_texts (name, text_content) VALUES (?, ?)
            """,
            (name, text),
        )
        self.connection.commit()

    def get_names_of_extracted_texts(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM extracted_texts")
        filenames = cursor.fetchall()
        return [filename[0] for filename in filenames]

    def name_exists(self, name):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT EXISTS(SELECT 1 FROM extracted_texts WHERE name = ?)
            """,
            (name,),
        )
        exists = cursor.fetchone()[0]
        return bool(exists)

    def delete_extracted_texts_bulk(self, names):
        if not names:
            return
        placeholders = ",".join("?" for _ in names)
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            DELETE FROM extracted_texts WHERE name IN ({placeholders})
            """,
            names,
        )
        self.connection.commit()
