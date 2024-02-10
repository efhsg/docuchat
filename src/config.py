import os
from pathlib import Path
from dotenv import load_dotenv


class Config:

    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parent.parent
    load_dotenv(project_root / ".env")

    UPLOAD_EXTENSIONS = ("pdf", "txt")

    @property
    def data_dir(self):
        data_dir = os.getenv("DATA_DIR", "data")
        return self.project_root / data_dir

    @property
    def db_path(self):
        return self.data_dir / "text_kb.sqlite"

    @property
    def logo_small_path(self):
        return str(self.current_file_path.parent / "img/logo_small.png")

    @classmethod
    def setup_directories(cls):
        # os.makedirs(cls().data_dir, mode=0o755, exist_ok=True)
        pass
