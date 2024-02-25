import tempfile
import os
import shutil
from pypdf import PdfReader
from epub2txt import epub2txt
from .interfaces.text_extractor import TextExtractor


class FileTextExtractor(TextExtractor):
    def __init__(self):
        self.extractors = {
            "pdf": self.extract_text_from_pdf,
            "txt": self.extract_text_from_txt,
            "epub": self.extract_text_from_epub,
        }

    def extract_text(self, uploaded_file):
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in self.extractors:
            return self.extractors[file_extension](uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'")

    @staticmethod
    def extract_text_from_pdf(uploaded_file):
        reader = PdfReader(uploaded_file)
        return "".join(page.extract_text() or "" for page in reader.pages)

    @staticmethod
    def extract_text_from_txt(uploaded_file):
        return uploaded_file.getvalue().decode("utf-8")

    @staticmethod
    def extract_text_from_epub(uploaded_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp_file:
            shutil.copyfileobj(uploaded_file, tmp_file)
            tmp_file_path = tmp_file.name
        extracted_text = epub2txt(tmp_file_path)
        os.remove(tmp_file_path)
        return extracted_text
