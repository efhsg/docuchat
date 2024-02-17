import unittest
from components.reader.zlib_text_compressor import ZlibTextCompressor


class TestZlibTextCompressor(unittest.TestCase):

    def test_compress_decompress(self):
        original_text = "This is a test string."
        compressor = ZlibTextCompressor()

        compressed_text = compressor.compress(original_text)
        decompressed_text = compressor.decompress(compressed_text)

        self.assertEqual(decompressed_text, original_text)


if __name__ == "__main__":
    unittest.main()
