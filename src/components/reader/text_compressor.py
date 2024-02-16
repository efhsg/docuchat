from abc import ABC, abstractmethod


class TextCompressor(ABC):

    @staticmethod
    @abstractmethod
    def compress(text):
        pass

    @staticmethod
    @abstractmethod
    def decompress(compressed_text):
        pass
