from .interfaces.logger import Logger
import logging
from logging import Logger as StandardLogger
import logging.config
from pathlib import Path
from shutil import copyfile


class NativeLogger(Logger):
    _logger = None
    _base_dir = Path(__file__).resolve().parent
    _example_config_path = _base_dir / "logging.example.ini"
    config_filename = _base_dir / "logging.ini"

    @classmethod
    def _get_config_path(cls):
        return cls._base_dir / cls.config_filename

    @classmethod
    def _prepare_config_file(cls, config_path):
        if not config_path.exists():
            copyfile(cls._example_config_path, config_path)

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
    def get_logger(name="docuchat") -> StandardLogger:
        NativeLogger._ensure_configured()
        return logging.getLogger(name)
