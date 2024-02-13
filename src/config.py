import os
from pathlib import Path
from dotenv import load_dotenv


class Config:

    current_file_path = Path(__file__).resolve()

    @property
    def project_root(self):
        return self.current_file_path.parent.parent

    def __init__(self):
        load_dotenv(self.project_root / ".env")

    UPLOAD_EXTENSIONS = ("pdf", "txt")

    @property
    def data_dir(self):
        data_dir = os.getenv("DATA_DIR", "data")
        return self.project_root / data_dir

    @property
    def logo_small_path(self):
        return str(self.project_root / "src/img/logo_small.png")

    @property
    def latest_migration_version(self):
        return "d0090ad818e3"
