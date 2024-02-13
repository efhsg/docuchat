from config import Config
from components.database.extract_text import ExtractText

config_instance = Config()


def file_already_exists(file_name):
    extract_text = ExtractText()
    return extract_text.name_exists(file_name)


def get_filenames_extracted_text():
    extract_text = ExtractText()
    filenames = extract_text.get_names_of_extracted_texts()
    return filenames


def save_extracted_text(text, filename):
    extract_text = ExtractText()
    extract_text.save_extracted_text_to_db(text, filename)


def delete_extracted_text_dict(file_dict):
    extract_text = ExtractText()
    filenames_to_delete = [
        file_name for file_name, is_checked in file_dict.items() if is_checked
    ]
    if filenames_to_delete:
        extract_text.delete_extracted_texts_bulk(filenames_to_delete)
