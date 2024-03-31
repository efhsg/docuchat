from abc import ABC, abstractmethod
import json
from typing import Any, Dict, List, Generator, Union
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Chatter(ABC):
    """
    An abstract base class defining the interface for a chat handler. This class provides
    the structure for processing and responding to messages using various chat models.
    """

    @abstractmethod
    def chat(
        self,
        messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = None,
        context_texts: List[str] = None,
    ) -> Union[str, Generator[str, None, None]]:
        """
        Abstract method to process messages and context, generating a response or series of responses.

        :param messages: A list of messages, which can include human messages, AI messages, and system messages.
        :param context_texts: Additional context provided as a list of strings to aid in generating responses.
        :return: A single response string or a generator yielding strings, depending on the implementation.
        """
        pass

    def get_configuration(self) -> Dict:
        """
        Retrieves the current configuration of the chatter instance, including its method name and parameters.

        :return: A dictionary containing the configuration details of the chatter instance.
        """
        return {"method": self.__class__.__name__, "params": self.get_params()}

    @abstractmethod
    def get_params(self) -> Dict:
        """
        Abstract method to get the parameters specific to the chatter implementation.

        :return: A dictionary of parameters used in the chatter configuration.
        """
        pass

    @abstractmethod
    def get_num_tokens(self, text: str) -> int:
        """
        Abstract method to calculate the number of tokens in the given text.

        :param text: The text for which to calculate the token count.
        :return: The number of tokens in the provided text.
        """
        pass

    @abstractmethod
    def get_num_tokens_left(self, text: str) -> int:
        """
        Abstract method to determine the number of tokens left that can be used, given the current text.

        :param text: The text to evaluate for the remaining token capacity.
        :return: The number of tokens left for further operations.
        """
        pass

    @abstractmethod
    def history_truncated_by(self) -> int:
        """
        Abstract method to get the number of messages truncated from history due to token limitations in the last operation.

        :return: The number of truncated messages from the history.
        """
        pass

    @abstractmethod
    def context_truncated_by(self) -> int:
        """
        Abstract method to get the number of context texts truncated due to token limitations in the last operation.

        :return: The number of truncated context texts.
        """
        pass

    @abstractmethod
    def get_total_tokens_used(self) -> int:
        """
        Abstract method to get the total number of tokens used in the last operation or chat session.

        :return: The total number of tokens used.
        """
        pass

    @abstractmethod
    def convert_messages_for_api(
        self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    ) -> List[Any]:
        """
        Abstract method to convert messages into a format suitable for the underlying chat API.

        :param messages: A list of messages including human, AI, and system messages.
        :return: A list of messages formatted for the chat API.
        """
        pass

    def sanitize_text_for_json(self, text: str) -> str:
        """
        Utility method to sanitize text for JSON encoding, ensuring that it is properly escaped.

        :param text: The text to be sanitized.
        :return: The sanitized text, suitable for JSON encoding.
        """
        sanitized_text = json.dumps(text)
        return sanitized_text.strip('"')
