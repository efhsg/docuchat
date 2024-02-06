import unittest
from unittest.mock import patch
from Extract_text import get_pdf_file_path, get_text_file_path
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


class GetTextFilePathTest(unittest.TestCase):
    @patch("Extract_text.Config")
    def test_get_text_file_path(self, mock_config):
        mock_config.TEXT_DIR = "/fake/text/dir"
        file_name = "document.pdf"
        expected_text_file_path = "/fake/text/dir/document.txt"
        result_path = get_text_file_path(file_name)
        self.assertEqual(expected_text_file_path, result_path)
