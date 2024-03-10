import zipfile
from typing import Callable, Dict
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
from .interfaces.text_extractor import TextExtractor


class FileTextExtractor(TextExtractor):
    def __init__(self):
        self.extractors: Dict[str, Callable[[BytesIO], str]] = {
            "pdf": self.extract_text_from_pdf,
            "txt": self.extract_text_from_txt,
            "epub": self.extract_text_from_epub,
        }

    def extract_text(self, uploaded_file: BytesIO) -> str:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in self.extractors:
            return self.extractors[file_extension](uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'")

    @staticmethod
    def extract_text_from_pdf(uploaded_file: BytesIO) -> str:
        reader = PdfReader(uploaded_file)
        return "".join(page.extract_text() or "" for page in reader.pages)

    @staticmethod
    def extract_text_from_txt(uploaded_file: BytesIO) -> str:
        return uploaded_file.getvalue().decode("utf-8")

    @staticmethod
    def extract_text_from_epub(uploaded_file: BytesIO) -> str:
        text = ""
        with zipfile.ZipFile(uploaded_file) as zf:
            for item in zf.infolist():
                if item.filename.endswith(".xhtml") or item.filename.endswith(".html"):
                    with zf.open(item) as file:
                        soup = BeautifulSoup(file, "html.parser")
                        text += soup.get_text(separator=" ", strip=True)
        return text
