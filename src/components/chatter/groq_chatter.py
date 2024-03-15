import os
from groq import Groq
from typing import Dict, List, Tuple

from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger


class GroqChatter(Chatter):
    def __init__(
        self,
        logger: StandardLogger = None,
        groq_model: str = "llama2-70b-4096",
        temperature: float = 0.5,
    ):
        self.model = groq_model
        self.temperature = temperature
        self.logger = logger

    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    }
                ],
                model=self.model,
                temperature=self.temperature,
            )
            if self.logger:
                self.logger.info(
                    f"Chatting with Groq model {self.model} at temperature {self.temperature}"
                )
            return chat_completion.choices[0].message.content
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during chat with Groq model: {e}")
            return "An error occurred while generating the response."

    def get_params(self) -> Dict:
        return {"model": self.model, "temperature": self.temperature}
