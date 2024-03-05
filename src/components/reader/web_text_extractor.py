from .interfaces.text_extractor import TextExtractor
import requests
from bs4 import BeautifulSoup
from logging import Logger as StandardLogger


class WebTextExtractor(TextExtractor):

    def __init__(
        self,
        logger: StandardLogger = None,
    ):
        self.logger = logger

    def extract_text(self, source):
        try:
            response = requests.get(source)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join(soup.stripped_strings)
            return text
        except requests.RequestException as e:
            self.logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to extract text from URL {source} due to: {e}")
            raise
