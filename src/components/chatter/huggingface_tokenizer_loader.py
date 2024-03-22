from functools import lru_cache
from transformers import AutoTokenizer

from components.chatter.interfaces.tokenizer_loader import TokenizerLoader
from utils.env_utils import getenv


class HuggingfaceTokenizerLoader(TokenizerLoader):

    def __init__(
        self,
        identifier: str = None,
    ):
        self.identifier = identifier

    @lru_cache(maxsize=128)
    def load(self) -> AutoTokenizer:
        return AutoTokenizer.from_pretrained(
            self.identifier, use_auth_token=getenv("HUGGINGFACEHUB_API_TOKEN")
        )
