from typing import Dict, List, Tuple

from components.chatter.interfaces.chatter import Chatter
from sqlalchemy.orm import Session
from logging import Logger as StandardLogger


class OpenAIChatter(Chatter):
    def __init__(
        self,
        logger: StandardLogger = None,
        open_ai_model: str = "gpt-4",
        temperature: float = 0.7,
    ):
        self.model = open_ai_model
        self.temperature = temperature
        self.logger = logger

    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        response = f"This is a hypothetical response from {self.model} to the query."
        if self.logger:
            self.logger.info(
                f"Chatting with model {self.model} at temperature {self.temperature}"
            )
        return response

    def get_params(self) -> Dict:
        return {"model": self.model, "temperature": self.temperature}
