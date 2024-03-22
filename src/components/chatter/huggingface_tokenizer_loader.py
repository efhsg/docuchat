from functools import lru_cache
from transformers import AutoTokenizer

from components.chatter.interfaces.tokenizer_loader import TokenizerLoader
from utils.env_utils import getenv


class HuggingfaceTokenizerLoader(TokenizerLoader):
    @lru_cache(maxsize=128)
    def load(self, model_identifier: str) -> AutoTokenizer:
        api_token = getenv("HUGGINGFACEHUB_API_TOKEN")
        return AutoTokenizer.from_pretrained(model_identifier, use_auth_token=api_token)
