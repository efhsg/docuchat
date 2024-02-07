from unittest import TestCase, mock
from unittest.mock import patch, MagicMock, mock_open
from components.reader.extract_text import (
    get_pdf_file_path,
    get_text_file_path,
    ensure_upload_dir,
    extract_text,
    extract_text_from_pdf,
    extract_text_from_txt,
    save_text_file,
    get_files_upload_dir_by_extension,
    delete_file_and_extracted_text,
    delete_files,
)
import logging

logger = logging.getLogger(__name__)


class TestEnsureUploadDir(TestCase):
    @patch("components.reader.extract_text.os.makedirs")
    @patch("components.reader.extract_text.os.path.exists")
    @patch("components.reader.extract_text.Config")
    def test_ensure_upload_dir(self, mock_config, mock_exists, mock_makedirs):
        mock_config.UPLOAD_DIR = "/fake/upload/dir"
        mock_config.TEXT_DIR = "/fake/text/dir"

        # Scenario 1: Both directories do not exist
        mock_exists.side_effect = [
            False,
            False,
        ]

        ensure_upload_dir()

        self.assertEqual(mock_makedirs.call_count, 2)
        mock_makedirs.assert_any_call("/fake/upload/dir")
        mock_makedirs.assert_any_call("/fake/text/dir")

        mock_makedirs.reset_mock()

        # Scenario 2: Both directories already exist
        mock_exists.side_effect = [True, True]

        ensure_upload_dir()

        mock_makedirs.assert_not_called()


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

        # Test PDF extraction
        result_pdf = extract_text(mock_uploaded_file_pdf)
        mock_extract_pdf.assert_called_once_with(mock_uploaded_file_pdf)
        self.assertEqual(result_pdf, "Extracted PDF content")

        # Test TXT extraction
        result_txt = extract_text(mock_uploaded_file_txt)
        mock_extract_txt.assert_called_once_with(mock_uploaded_file_txt)
        self.assertEqual(result_txt, "Extracted TXT content")

    def test_extract_text_unsupported_file_type(self):
        # Mock the uploaded_file object with unsupported file extension
        mock_uploaded_file_unsupported = mock.MagicMock()
        mock_uploaded_file_unsupported.name = "test.unsupported"

        # Test unsupported file type raises ValueError
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


class TestSaveTextFile(TestCase):
    @patch("components.reader.extract_text.os.path.exists", return_value=False)
    @patch("components.reader.extract_text.open", new_callable=mock_open, create=True)
    def test_save_text_file(self, mock_file_open, mock_exists):
        text = "Sample text"
        file_path = "/fake/path/to/text_file.txt"

        save_text_file(text, file_path)

        mock_exists.assert_called_once_with(file_path)
        mock_file_open.assert_called_once_with(file_path, "w", encoding="utf-8")
        mock_file_open().write.assert_called_once_with(text)


class FilePathTest(TestCase):
    @patch("components.reader.extract_text.Config")
    def test_get_pdf_file_path(self, mock_config):
        mock_config.UPLOAD_DIR = "/fake/upload/dir"

        file_name = "test.pdf"
        expected_path = "/fake/upload/dir/test.pdf"

        result_path = get_pdf_file_path(file_name)
        self.assertEqual(expected_path, result_path)

    @patch("components.reader.extract_text.Config")
    def test_get_text_file_path(self, mock_config):
        mock_config.TEXT_DIR = "/fake/text/dir"
        file_name = "document.pdf"
        expected_text_file_path = "/fake/text/dir/document.txt"
        result_path = get_text_file_path(file_name)
        self.assertEqual(expected_text_file_path, result_path)


class TestGetFilesUploadDirByExtension(TestCase):
    @patch("components.reader.extract_text.os.listdir")
    @patch("components.reader.extract_text.Config")
    def test_get_files_upload_dir_by_extension(self, mock_config, mock_listdir):

        mock_config.UPLOAD_DIR = "/fake/upload/dir"
        mock_config.UPLOAD_EXTENSIONS = (".txt", ".pdf")
        mock_listdir.return_value = [
            "document1.txt",
            "image.jpg",
            "document2.pdf",
            "archive.zip",
        ]

        result_files = get_files_upload_dir_by_extension()

        expected_files = ["document1.txt", "document2.pdf"]
        self.assertEqual(result_files, expected_files)
        mock_listdir.assert_called_once_with("/fake/upload/dir")


class TestDeleteFileAndExtractedText(TestCase):
    @patch("components.reader.extract_text.os.remove")
    @patch("components.reader.extract_text.os.path.join")
    @patch("components.reader.extract_text.get_text_file_path")
    @patch("components.reader.extract_text.Config")
    def test_delete_file_and_extracted_text(
        self, mock_config, mock_get_text_file_path, mock_path_join, mock_remove
    ):

        mock_config.UPLOAD_DIR = "/fake/upload/dir"
        file_name = "testfile.txt"
        text_file_path = "/fake/text/dir/testfile.txt"
        mock_get_text_file_path.return_value = text_file_path

        # Case 1: delete_text is False
        delete_file_and_extracted_text(file_name, False)
        mock_path_join.assert_called_once_with("/fake/upload/dir", file_name)
        mock_remove.assert_called_once_with(mock_path_join.return_value)
        mock_get_text_file_path.assert_not_called()
        mock_remove.reset_mock()
        mock_path_join.reset_mock()

        # Case 2: delete_text is True
        delete_file_and_extracted_text(file_name, True)
        self.assertEqual(mock_path_join.call_count, 1)
        mock_get_text_file_path.assert_called_once_with(file_name)
        self.assertEqual(mock_remove.call_count, 2)


class TestDeleteFiles(TestCase):
    @patch("components.reader.extract_text.delete_file_and_extracted_text")
    def test_delete_files(self, mock_delete_file_and_extracted_text):
        file_dict = {
            "file1.txt": True,
            "file2.pdf": False,
            "file3.txt": True,
        }
        delete_extracted_text = True

        delete_files(file_dict, delete_extracted_text)

        self.assertEqual(mock_delete_file_and_extracted_text.call_count, 2)
        mock_delete_file_and_extracted_text.assert_any_call(
            "file1.txt", delete_extracted_text
        )
        mock_delete_file_and_extracted_text.assert_any_call(
            "file3.txt", delete_extracted_text
        )

        calls = [call[0] for call in mock_delete_file_and_extracted_text.call_args_list]
        self.assertNotIn(("file2.pdf", delete_extracted_text), calls)
