import os
from pathlib import Path
from dotenv import load_dotenv

from utils.env_utils import getenv


class Config:
    _current_file_path = Path(__file__).resolve()

    def __init__(self):
        load_dotenv(self.project_root / ".env")

    @property
    def project_root(self):
        return self._current_file_path.parent.parent

    @property
    def upload_extensions(self):
        return ("epub", "pdf", "txt")

    @property
    def data_dir(self):
        data_dir = os.getenv("DATA_DIR", "data")
        return self.project_root / data_dir

    @property
    def logo_small_path(self):
        return str(self.project_root / "src/img/logo_small_v2.1.png")

    @property
    def model_cache_dir(self):
        return str(getenv("MODEL_CACHE_DIR", self.project_root / "data/models"))

    @property
    def latest_migration_version(self):
        return "cdf9b87e5fb0"
