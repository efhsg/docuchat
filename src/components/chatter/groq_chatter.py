from groq import Groq
from typing import Dict, List, Tuple, Optional

from components.chatter.interfaces.chatter import Chatter
from logging import Logger as StandardLogger

from utils.env_utils import getenv


class GroqChatter(Chatter):
    def __init__(
        self,
        logger: StandardLogger = None,
        groq_model: str = "llama2-70b-4096",
        temperature: float = 0.5,
        max_tokens: int = 1024,
        top_p: float = 1,
        stream: bool = True,
        stop: Optional[str] = None,
    ):
        self.model = groq_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop

        self.logger = logger

    def chat(self, query: str, context: Dict[str, List[Tuple[str, float]]]) -> str:
        client = Groq(api_key=getenv("GROQ_API_KEY"))
        try:
            stream_response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "you are a helpful assistant."},
                    {"role": "user", "content": query},
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=self.stream,
                stop=[self.stop] if self.stop else None,
            )

            response_content = ""
            for chunk in stream_response:
                if chunk.choices[0].delta.content is not None:
                    response_content += chunk.choices[0].delta.content

            if self.logger:
                self.logger.info(
                    f"Chatting with Groq model {self.model} at temperature {self.temperature}, max tokens {self.max_tokens}, top_p {self.top_p}, stream {str(self.stream)}, stop '{self.stop}'"
                )
            return response_content
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during chat with Groq model: {e}")
            return f"An error occurred while generating the response: {e}"

    def get_params(self) -> Dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "stop": self.stop,
        }
