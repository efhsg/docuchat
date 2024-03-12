from typing import Dict, List, Tuple

from components.chatter.interfaces.chatter import Chatter
from sqlalchemy.orm import Session
from logging import Logger as StandardLogger


class GPT4Chatter(Chatter):
    def __init__(self, logger: StandardLogger = None, temperature: float = 0.7):
        self.temperature = temperature

    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        response = "This is a hypothetical GPT-4 response to the query."
        return response

    def get_params(self) -> Dict:
        return {"temperature": self.temperature}
