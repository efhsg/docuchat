from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
from components.reader.extract_text import (
    extract_text,
    extract_text_from_pdf,
    extract_text_from_txt,
)
import logging

logger = logging.getLogger(__name__)


class TestExtractText(TestCase):
    @patch("components.reader.extract_text.extract_text_from_pdf")
    @patch("components.reader.extract_text.extract_text_from_txt")
    def test_extract_text_supported_file_types(
        self, mock_extract_txt, mock_extract_pdf
    ):
        mock_uploaded_file_pdf = mock.MagicMock()
        mock_uploaded_file_pdf.name = "test.pdf"

        mock_uploaded_file_txt = mock.MagicMock()
        mock_uploaded_file_txt.name = "test.txt"

        mock_extract_pdf.return_value = "Extracted PDF content"
        mock_extract_txt.return_value = "Extracted TXT content"

        result_pdf = extract_text(mock_uploaded_file_pdf)
        mock_extract_pdf.assert_called_once_with(mock_uploaded_file_pdf)
        self.assertEqual(result_pdf, "Extracted PDF content")

        result_txt = extract_text(mock_uploaded_file_txt)
        mock_extract_txt.assert_called_once_with(mock_uploaded_file_txt)
        self.assertEqual(result_txt, "Extracted TXT content")

    def test_extract_text_unsupported_file_type(self):
        mock_uploaded_file_unsupported = mock.MagicMock()
        mock_uploaded_file_unsupported.name = "test.unsupported"

        with self.assertRaises(ValueError) as context:
            extract_text(mock_uploaded_file_unsupported)

        self.assertTrue(
            "Unsupported file type: 'unsupported'" in str(context.exception)
        )


class TestExtractTextFromPDF(TestCase):
    @patch("components.reader.extract_text.PdfReader")
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text"
        mock_pdf_reader.return_value.pages = [mock_page]

        mock_uploaded_file = MagicMock()
        result_text = extract_text_from_pdf(mock_uploaded_file)

        self.assertEqual(result_text, "Sample text")
        mock_pdf_reader.assert_called_once_with(mock_uploaded_file)
        mock_page.extract_text.assert_called_once()


class TestExtractTextFromTXT(TestCase):
    def test_extract_text_from_txt(self):
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.getvalue.return_value = b"Sample text in bytes"

        result_text = extract_text_from_txt(mock_uploaded_file)

        self.assertEqual(result_text, "Sample text in bytes")
        mock_uploaded_file.getvalue.assert_called_once()
