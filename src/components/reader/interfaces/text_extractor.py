from abc import ABC, abstractmethod
from typing import Any


class TextExtractor(ABC):

    @abstractmethod
    def extract_text(self, source: Any) -> str:
        """Extracts text from an uploaded file."""
        pass
