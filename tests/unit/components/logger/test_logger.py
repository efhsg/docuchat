import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from components.logger.logger import Logger


class TestLogger(unittest.TestCase):

    @patch("pathlib.Path.exists")
    def test_prepare_config_file_does_nothing_if_exists(self, mock_exists):
        mock_exists.return_value = True

        with patch("shutil.copyfile") as mock_copyfile:
            config_path = Logger._get_config_path()
            Logger._prepare_config_file(config_path)

            mock_copyfile.assert_not_called()

    @patch("logging.config.fileConfig")
    def test_load_config(self, mock_fileconfig):
        config_path = Logger._get_config_path()
        Logger._load_config(config_path)
        mock_fileconfig.assert_called_once_with(
            str(config_path), disable_existing_loggers=False
        )

    @patch("components.logger.logger.Logger._load_config")
    @patch("components.logger.logger.Logger._prepare_config_file")
    @patch("components.logger.logger.Logger._get_config_path")
    def test_ensure_configured_sets_logger(
        self, mock_get_config_path, mock_prepare_config_file, mock_load_config
    ):
        Logger._logger = None

        config_path = Logger._get_config_path()
        mock_get_config_path.return_value = config_path

        Logger._ensure_configured()

        self.assertIsNotNone(Logger._logger)
        mock_prepare_config_file.assert_called_once_with(config_path)
        mock_load_config.assert_called_once_with(config_path)

    @patch("logging.getLogger")
    def test_get_logger(self, mock_getLogger):
        Logger._logger = None

        Logger.get_logger("test_logger")

        mock_getLogger.assert_any_call("test_logger")
