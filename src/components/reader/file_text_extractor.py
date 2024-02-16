from pypdf import PdfReader
from .text_extractor import TextExtractor


class FileTextExtractor(TextExtractor):
    def __init__(self):
        self.extractors = {
            "pdf": self.extract_text_from_pdf,
            "txt": self.extract_text_from_txt,
            # Potentially more mappings for other file types
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
