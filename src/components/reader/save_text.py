import os
from config import Config
from database_manager import DatabaseManager

config_instance = Config()


def file_already_exists(file_name):
    db_manager = DatabaseManager()
    return db_manager.name_exists(file_name)


def get_filenames_extracted_text():
    db_manager = DatabaseManager()
    filenames = db_manager.get_names_of_extracted_texts()
    return filenames


def save_extracted_text(text, filename):
    db_manager = DatabaseManager()
    db_manager.save_extracted_text_to_db(text, filename)


def delete_extracted_text_dict(file_dict):
    db_manager = DatabaseManager()
    filenames_to_delete = [
        file_name for file_name, is_checked in file_dict.items() if is_checked
    ]
    if filenames_to_delete:
        db_manager.delete_extracted_texts_bulk(filenames_to_delete)
