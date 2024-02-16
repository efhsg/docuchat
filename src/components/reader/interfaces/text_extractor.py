from abc import ABC, abstractmethod


class TextExtractor(ABC):

    @abstractmethod
    def extract_text(self, uploaded_file):
        """Extracts text from an uploaded file."""
        pass
