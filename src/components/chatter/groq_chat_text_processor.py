from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from components.chatter.interfaces.tokenizer_loader import TokenizerLoader


class GroqChatTextProcessor(ChatTextProcessor):
    def __init__(self, tokenizer_loader: TokenizerLoader, context_window: int):
        self.tokenizer_loader = tokenizer_loader
        self.context_window = context_window

    def reduce_texts(
        self,
        messages: List[Dict[str, str]],
        context_texts: List[str],
        response_buffer: int = 512,
    ) -> Tuple[List[Dict[str, str]], List[str], int]:
        effective_context_window = self.context_window - response_buffer
        total_tokens = 0
        reduced_messages = []
        reduced_texts = []

        for message in reversed(messages):
            message_str = str(message)
            message_tokens = self.get_num_tokens(message_str)
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

    def get_num_tokens(self, text: str) -> int:
        tokenizer = self.tokenizer_loader.load("huggingface_identifier")
        return len(tokenizer.encode(text))
