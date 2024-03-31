from typing import List, Dict, Optional, Tuple
from logging import Logger as StandardLogger
from components.chatter.interfaces.chat_text_processor import ChatTextProcessor
from transformers import AutoTokenizer


class GroqChatTextProcessor(ChatTextProcessor):
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_window: int = 4096,
        logger: Optional[StandardLogger] = None,
    ):
        self.tokenizer = tokenizer
        self.context_window = context_window
        self.logger = logger

    def reduce_texts(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
        response_buffer: int = 512,
    ) -> Tuple[List[Dict[str, str]], List[str], int]:

        messages = messages or []
        context_texts = context_texts or []
        latest_message_tokens = (
            self.get_num_tokens(str(messages[-1])) if messages else 0
        )
        effective_context_window = (
            self.context_window - response_buffer - latest_message_tokens
        )
        total_tokens = 0
        reduced_messages, reduced_texts = [], []

        for text in reversed(context_texts):
            text_tokens = self.get_num_tokens(text)
            if total_tokens + text_tokens > effective_context_window:
                break
            reduced_texts.insert(0, text)
            total_tokens += text_tokens
        for message in reversed(messages[:-1]):
            message_tokens = self.get_num_tokens(str(message))
            if total_tokens + message_tokens > effective_context_window:
                break
            reduced_messages.insert(0, message)
            total_tokens += message_tokens

        if messages:
            reduced_messages.append(messages[-1])
            total_tokens += latest_message_tokens

        return reduced_messages, reduced_texts, total_tokens

    def get_num_tokens(
        self,
        text: Optional[str],
    ) -> int:
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def get_num_tokens_left(
        self,
        messages: List[Dict[str, str]] = None,
        context_texts: List[str] = None,
    ) -> int:
        _, _, total_used_tokens = self.reduce_texts(
            messages=messages,
            context_texts=context_texts,
        )
        return self.context_window - total_used_tokens

    @property
    def context_window(self) -> int:
        return self._context_window

    @context_window.setter
    def context_window(self, value: int):
        if value < 0:
            raise ValueError("context_window must be non-negative")
        self._context_window = value

    def prepare_log_message(self, messages: List[Dict[str, str]]) -> str:
        truncated_messages = [
            {k: (v[:10] if i == 1 else v) for i, (k, v) in enumerate(message.items())}
            for message in messages
        ]
        return str(truncated_messages)
