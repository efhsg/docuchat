import zlib


class TextCompression:
    @staticmethod
    def compress(text):
        return zlib.compress(text.encode("utf-8"))

    @staticmethod
    def decompress(compressed_text):
        return zlib.decompress(compressed_text).decode("utf-8")
