from unittest import TestCase
from unittest.mock import patch


class TestEnsureUploadDir(TestCase):
    # @patch("components.reader.save_text.os.makedirs")
    # @patch("components.reader.save_text.os.path.exists")
    # @patch("components.reader.save_text.Config")
    # def test_ensure_data_dir(self, mock_config, mock_exists, mock_makedirs):
    #     mock_config.DATA_DIR = "/fake/data/dir"
    #     # Scenario 1: directory does not exist
    #     mock_exists.side_effect = [False]

    #     ensure_data_dir()

    #     self.assertEqual(mock_makedirs.call_count, 1)
    #     mock_makedirs.assert_any_call("/fake/data/dir")

    #     mock_makedirs.reset_mock()

    #     # Scenario 2: Both directories already exist
    #     mock_exists.side_effect = [True]

    #     ensure_data_dir()

    #     mock_makedirs.assert_not_called()
    pass
