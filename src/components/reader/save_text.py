import os
from Config import Config


def ensure_data_dir():
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)


def extracted_text_already_exists(file_name):
    base_name = os.path.splitext(file_name)[0]
    return any(f.startswith(base_name) for f in get_extracted_data())


def get_extracted_data():
    all_files = os.listdir(Config.DATA_DIR)
    return [file for file in all_files if file.lower().endswith("txt")]


def save_file_to_text(text, file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)


def get_text_file_path(file_name):
    file_name_without_extension = file_name.rsplit(".", 1)[0]
    return os.path.join(Config.DATA_DIR, file_name_without_extension + ".txt")


def delete_extracted_text(name):
    try:
        os.remove(Config.DATA_DIR / name)
    except FileNotFoundError:
        pass


def delete_extracted_text_dict(file_dict):
    for file_name, is_checked in file_dict.items():
        if is_checked:
            delete_extracted_text(file_name)
