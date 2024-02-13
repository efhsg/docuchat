import logging
import logging.config
import os
from pathlib import Path
from shutil import copyfile


class Logger:
    _logger = None
    _base_dir = Path(__file__).resolve().parent
    _example_config_path = _base_dir / "logging.example.ini"

    @classmethod
    def _get_config_path(cls):
        config_filename = "logging.ini"
        return cls._base_dir / config_filename

    @classmethod
    def _prepare_config_file(cls, config_path):
        if not config_path.exists():
            copyfile(cls._example_config_path, config_path)

            logs_dir = os.environ.get("LOGS_DIR", "data/logs")
            logs_dir_path = Path(logs_dir)
            os.makedirs(logs_dir_path, exist_ok=True)

            with open(config_path, "r") as file:
                config_content = file.read()

            config_content = config_content.replace(
                "docuchat.log", str(logs_dir_path / "docuchat.log")
            )
            config_content = config_content.replace(
                "docuchat_errors.log", str(logs_dir_path / "docuchat_errors.log")
            )

            with open(config_path, "w") as file:
                file.write(config_content)

    @classmethod
    def _load_config(cls, config_path):
        logging.config.fileConfig(str(config_path), disable_existing_loggers=False)

    @classmethod
    def _ensure_configured(cls):
        if cls._logger is None:
            config_path = cls._get_config_path()
            cls._prepare_config_file(config_path)
            cls._load_config(config_path)
            cls._logger = True

    @staticmethod
    def get_logger(name="docuchat"):
        Logger._ensure_configured()
        return logging.getLogger(name)
