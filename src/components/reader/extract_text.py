import os
from Config import Config
from pypdf import PdfReader


def ensure_upload_dir():
    if not os.path.exists(Config.UPLOAD_DIR):
        os.makedirs(Config.UPLOAD_DIR)
    if not os.path.exists(Config.TEXT_DIR):
        os.makedirs(Config.TEXT_DIR)


def file_already_exists(file_name):
    base_name = os.path.splitext(file_name)[0]
    return any(f.startswith(base_name) for f in get_files_upload_dir_by_extension())


def save_pdf_file(uploaded_file, file_path):
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())


def extract_text(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    extractors = {
        "pdf": extract_text_from_pdf,
        "txt": extract_text_from_txt,
    }
    if file_extension in extractors:
        return extractors[file_extension](uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: '{file_extension}'")


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_txt(uploaded_file):
    return uploaded_file.getvalue().decode("utf-8")


def save_text_file(text, file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)


def get_pdf_file_path(file_name):
    return os.path.join(Config.UPLOAD_DIR, file_name)


def get_text_file_path(file_name):
    file_name_without_extension = file_name.rsplit(".", 1)[0]
    return os.path.join(Config.TEXT_DIR, file_name_without_extension + ".txt")


def get_files_upload_dir_by_extension():
    all_files = os.listdir(Config.UPLOAD_DIR)
    return [
        file for file in all_files if file.lower().endswith(Config.UPLOAD_EXTENSIONS)
    ]


def delete_file_and_extracted_text(file_name, delete_text):
    try:
        os.remove(os.path.join(Config.UPLOAD_DIR, file_name))
    except FileNotFoundError:
        pass
    if delete_text:
        try:
            os.remove(get_text_file_path(file_name))
        except FileNotFoundError:
            pass


def delete_files(file_dict, delete_extracted_text):
    for file, is_checked in file_dict.items():
        if is_checked:
            delete_file_and_extracted_text(file, delete_extracted_text)
