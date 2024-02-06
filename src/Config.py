import os
from pathlib import Path


class Config:
    UPLOAD_EXTENSIONS = ("pdf", "txt")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "upload")
    TEXT_DIR = os.getenv("TEXT_DIR", UPLOAD_DIR + "/extracted_text")

    current_file_path = Path(__file__).resolve()
    logo_small_path = str(current_file_path.parent / "img/logo_small.png")
