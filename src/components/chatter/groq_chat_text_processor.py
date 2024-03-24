from typing import List, Dict, Tuple

from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from transformers import AutoTokenizer


class GroqChatTextProcessor(ChatTextProcessor):
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_window: int = 4096,
    ):
        self.tokenizer = tokenizer
        self.context_window = context_window

    def reduce_texts(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
        response_buffer: int = 512,
    ) -> Tuple[List[Dict[str, str]], List[str], int]:
        messages = messages or []
        context_texts = context_texts or []

        effective_context_window = self.context_window - response_buffer
        total_tokens = 0
        reduced_messages, reduced_texts = [], []

        for message in reversed(messages):
            message_tokens = self.get_num_tokens(str(message))
            if total_tokens + message_tokens > effective_context_window:
                break
            reduced_messages.insert(0, message)
            total_tokens += message_tokens

        for text in reversed(context_texts):
            text_tokens = self.get_num_tokens(text)
            if total_tokens + text_tokens > effective_context_window:
                break
            reduced_texts.insert(0, text)
            total_tokens += text_tokens

        return reduced_messages, reduced_texts, total_tokens

    def get_num_tokens(
        self,
        text: str,
    ) -> int:
        return len(self.tokenizer.encode(text))

    def get_num_tokens_left(self, messages: List[Dict[str, str]]) -> int:
        _, _, total_used_tokens = self.reduce_texts(
            messages=messages,
        )
        return self.context_window - total_used_tokens

    @property
    def context_window(self) -> int:
        return self._context_window

    @context_window.setter
    def context_window(self, value: int):
        """Set the context window size, ensuring it meets requirements."""
        if value < 0:
            raise ValueError("context_window must be non-negative")
        self._context_window = value
