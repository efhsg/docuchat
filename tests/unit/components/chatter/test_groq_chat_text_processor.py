import unittest
from unittest.mock import MagicMock
from components.chatter.groq_chat_text_processor import GroqChatTextProcessor
from components.chatter.interfaces.tokenizer_loader import TokenizerLoader


class TestGroqChatTextProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_tokenizer_loader = MagicMock(spec=TokenizerLoader)
        self.processor = GroqChatTextProcessor(
            tokenizer_loader=self.mock_tokenizer_loader
        )

    def test_reduce_texts_empty_inputs(self):
        messages, context_texts, response_buffer = [], [], 512
        expected_output = ([], [], 0)

        output = self.processor.reduce_texts(messages, context_texts, response_buffer)
        self.assertEqual(output, expected_output)

    def test_get_num_tokens(self):
        text = "This is a test string."
        expected_token_count = len(text.split())
        self.mock_tokenizer_loader.load.return_value.encode.return_value = text.split()

        token_count = self.processor.get_num_tokens(text)
        self.assertEqual(token_count, expected_token_count)


if __name__ == "__main__":
    unittest.main()
