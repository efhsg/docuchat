from abc import ABC, abstractmethod


class TextExtractor(ABC):

    @abstractmethod
    def extract_text(self, source):
        """Extracts text from an uploaded file."""
        pass
