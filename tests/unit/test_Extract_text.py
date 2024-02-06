import unittest
from unittest.mock import patch
from Extract_text import get_pdf_file_path
import logging

logger = logging.getLogger(__name__)


class GetPdfFilePathTest(unittest.TestCase):
    @patch("Extract_text.Config")
    def test_get_pdf_file_path(self, mock_config):
        mock_config.UPLOAD_DIR = "/fake/upload/dir"

        file_name = "test.pdf"
        expected_path = "/fake/upload/dir/test.pdf"

        result_path = get_pdf_file_path(file_name)
        self.assertEqual(expected_path, result_path)
