from abc import ABC, abstractmethod
from transformers import AutoTokenizer


class TokenizerLoader(ABC):

    @abstractmethod
    def load(self, model_identifier: str) -> AutoTokenizer: ...
