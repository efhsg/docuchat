import zlib
from components.reader.text_compressor import TextCompressor


class ZlibTextCompressor(TextCompressor):

    @staticmethod
    def compress(text):
        return zlib.compress(text.encode("utf-8"))

    @staticmethod
    def decompress(compressed_text):
        return zlib.decompress(compressed_text).decode("utf-8")
