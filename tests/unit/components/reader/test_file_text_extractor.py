from unittest import TestCase
from unittest.mock import patch, MagicMock
from components.reader.file_text_extractor import FileTextExtractor


class TestFileTextExtractor(TestCase):

    def setUp(self):
        self.text_extractor = FileTextExtractor()

    @patch("components.reader.file_text_extractor.PdfReader")
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text"
        mock_pdf_reader.return_value.pages = [mock_page]

        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "document.pdf"
        mock_uploaded_file.read.return_value = b"%PDF-1.4 example PDF content"

        result_text = self.text_extractor.extract_text(mock_uploaded_file)
        self.assertEqual(result_text, "Sample text")

    def test_extract_text_from_txt(self):
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "document.txt"
        mock_uploaded_file.getvalue.return_value = b"Sample text in bytes"

        result_text = self.text_extractor.extract_text(mock_uploaded_file)
        self.assertEqual(result_text, "Sample text in bytes")

    def test_extract_text_supported_file_types(self):
        with patch(
            "components.reader.file_text_extractor.PdfReader"
        ) as mock_pdf_reader:
            mock_pdf_reader.return_value.pages = [
                MagicMock(extract_text=MagicMock(return_value="PDF content"))
            ]
            mock_uploaded_file_pdf = MagicMock()
            mock_uploaded_file_pdf.name = "test.pdf"
            mock_uploaded_file_pdf.read.return_value = b"PDF content"

            result_pdf = self.text_extractor.extract_text(mock_uploaded_file_pdf)
            self.assertIn("PDF content", result_pdf)

        mock_uploaded_file_txt = MagicMock()
        mock_uploaded_file_txt.name = "test.txt"
        mock_uploaded_file_txt.getvalue.return_value = b"TXT content"

        result_txt = self.text_extractor.extract_text(mock_uploaded_file_txt)
        self.assertEqual(result_txt, "TXT content")

    def test_extract_text_unsupported_file_type(self):
        mock_uploaded_file_unsupported = MagicMock()
        mock_uploaded_file_unsupported.name = "test.unsupported"
        mock_uploaded_file_unsupported.read.return_value = b"Unsupported content"

        with self.assertRaises(ValueError) as context:
            self.text_extractor.extract_text(mock_uploaded_file_unsupported)
        self.assertTrue(
            "Unsupported file type: 'unsupported'" in str(context.exception)
        )
