from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class ChatTextProcessor(ABC):

    @abstractmethod
    def reduce_texts(
        self,
        messages: List[Dict[str, str]],
        context_texts: List[str],
        response_buffer: int,
    ) -> Tuple[List[Dict[str, str]], List[str], int]:
        """
        Reduce texts and messages to fit within a specified context window, considering a response buffer.
        Returns the reduced messages, reduced context texts, and the total number of tokens for these reduced texts.
        """
        pass

    @abstractmethod
    def get_num_tokens(
        self,
        text: str,
    ) -> int:
        """
        Calculate the number of tokens in a given text.
        """
        pass
