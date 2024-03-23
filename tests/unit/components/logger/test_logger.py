import unittest
from unittest.mock import patch, mock_open
from components.logger.native_logger import NativeLogger


class TestLogger(unittest.TestCase):

    @patch("pathlib.Path.exists")
    def test_prepare_config_file_does_nothing_if_exists(self, mock_exists):
        mock_exists.return_value = True
        with patch("shutil.copyfile") as mock_copyfile:
            NativeLogger._prepare_config_file()
            mock_copyfile.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data="test data")
    @patch("components.logger.native_logger.NativeLogger._adjust_config_paths")
    @patch("logging.config.fileConfig")
    def test_load_config(self, mock_fileconfig, mock_adjust_config_paths, mock_open):
        mock_adjust_config_paths.return_value = "adjusted test data"
        NativeLogger._load_config()
        mock_fileconfig.assert_called()
        mock_adjust_config_paths.assert_called_once_with("test data")

    @patch("components.logger.native_logger.NativeLogger._load_config")
    @patch("components.logger.native_logger.NativeLogger._prepare_config_file")
    def test_ensure_configured_sets_logger(
        self, mock_prepare_config_file, mock_load_config
    ):
        NativeLogger._logger = None
        NativeLogger._ensure_configured()
        self.assertIsNotNone(NativeLogger._logger)
        mock_prepare_config_file.assert_called_once()
        mock_load_config.assert_called_once()

    @patch("logging.getLogger")
    def test_get_logger(self, mock_getLogger):
        NativeLogger.get_logger("test_logger")
        mock_getLogger.assert_called_with("test_logger")
