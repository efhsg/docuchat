import unittest
from unittest.mock import MagicMock
from components.chatter.groq_chat_text_processor import GroqChatTextProcessor


class TestGroqChatTextProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_tokenizer = MagicMock()
        self.mock_tokenizer.encode = MagicMock()

        self.processor = GroqChatTextProcessor(
            tokenizer=self.mock_tokenizer, context_window=4096
        )

    def test_reduce_texts_empty_inputs(self):
        messages, context_texts, response_buffer = [], [], 512
        expected_output = ([], [], 0)

        output = self.processor.reduce_texts(messages, context_texts, response_buffer)
        self.assertEqual(output, expected_output)

    def test_get_num_tokens(self):
        text = "This is a test string."
        expected_token_count = len(text.split())
        self.mock_tokenizer.encode.return_value = list(range(expected_token_count))

        token_count = self.processor.get_num_tokens(text)
        self.assertEqual(token_count, expected_token_count)


if __name__ == "__main__":
    unittest.main()
