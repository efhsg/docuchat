from configparser import ConfigParser
from io import StringIO
from logging import Logger
import logging.config
from pathlib import Path
from shutil import copyfile
import re


class NativeLogger(Logger):
    _logger = None
    _example_config_file = Path(__file__).resolve().parent / "logging.example.ini"
    _root_dir = Path(__file__).resolve().parents[3]
    _config_file = _root_dir / "logging.ini"

    @classmethod
    def _prepare_config_file(cls):
        if not cls._config_file.exists():
            copyfile(cls._example_config_file, cls._config_file)

    @classmethod
    def _adjust_config_paths(cls, config_str):
        def replacer(match):
            original_path = match.group(1)
            new_path = cls._root_dir / original_path
            return f"args=('{new_path}', 'a')"

        pattern = r"args=\('\s*([^']+)',\s*'a'\s*\)"
        adjusted_config_str = re.sub(pattern, replacer, config_str)

        return adjusted_config_str

    @classmethod
    def _load_config(cls):
        with open(cls._config_file, "r") as f:
            config_str = f.read()

        adjusted_config_str = cls._adjust_config_paths(config_str)

        config_stream = StringIO(adjusted_config_str)
        logging.config.fileConfig(config_stream, disable_existing_loggers=False)

    @classmethod
    def _ensure_configured(cls):
        if cls._logger is None:
            cls._prepare_config_file()
            cls._load_config()
            cls._logger = True

    @classmethod
    def get_logger(cls, name="docuchat") -> logging.Logger:
        cls._ensure_configured()
        return logging.getLogger(name)
