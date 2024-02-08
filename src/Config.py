import os
from pathlib import Path

from dotenv import load_dotenv


class Config:

    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parent.parent

    load_dotenv(project_root / ".env")

    UPLOAD_EXTENSIONS = ("pdf", "txt")
    DATA_DIR = project_root / os.getenv("DATA_DIR")

    logo_small_path = str(current_file_path.parent / "img/logo_small.png")
