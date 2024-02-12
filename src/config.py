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
        # This might be unused if you're switching entirely to MySQL
        return self.data_dir / "text_kb.sqlite"

    @property
    def logo_small_path(self):
        return str(self.current_file_path.parent / "img/logo_small.png")

    @property
    def db_host(self):
        running_in_docker = os.getenv("RUNNING_IN_DOCKER", "false") == "true"
        if running_in_docker:
            return os.getenv("DB_HOST_DOCKER", "mysql")
        else:
            return os.getenv("DB_HOST_VENV", "localhost")

    @property
    def db_user(self):
        return os.getenv("DB_USER")

    @property
    def db_password(self):
        return os.getenv("DB_PASSWORD")

    @property
    def db_name(self):
        return os.getenv("DB_NAME", "docuchatdb")

    @property
    def db_port(self):
        return os.getenv("DB_PORT", "3306")
