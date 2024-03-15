from typing import Any, Dict, List
import requests
from utils.env_utils import getenv
from components.chatter.openai_chatter import OpenAIChatter
from components.chatter.groq_chatter import GroqChatter
from logging import Logger as StandardLogger


class ModelOptionsFetchError(Exception):
    pass


class ChatterConfig:
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 1.0
    OPEN_API_MODEL_DEFAULT = getenv("OPEN_API_MODEL_DEFAULT", "gpt-4")
    GROQ_API_MODEL_DEFAULT = getenv("GROQ_API_MODEL_DEFAULT", "llama2-70b-4096")

    chatter_classes = {
        "OpenAI": OpenAIChatter,
        "Groq": GroqChatter,
    }

    def __init__(self, logger: StandardLogger = None):
        self.logger = logger
        self.model_options = self.fetch_model_options()
        self.groq_model_options = [
            "llama2-70b-4096",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
        ]
        self.base_field_definitions = {
            "temperature": {
                "label": "Response Generation Temperature",
                "type": "number",
                "default": float(getenv("CHATTER_TEMPERATURE_DEFAULT", "0.7")),
                "options": [],
            },
            "open_ai_model": {
                "label": "Model",
                "type": "select",
                "options": self.model_options,
                "default": (
                    self.OPEN_API_MODEL_DEFAULT
                    if self.OPEN_API_MODEL_DEFAULT in self.model_options
                    else None
                ),
            },
            "groq_model": {
                "label": "Groq Model",
                "type": "select",
                "options": self.groq_model_options,
                "default": (
                    self.GROQ_API_MODEL_DEFAULT
                    if self.GROQ_API_MODEL_DEFAULT in self.groq_model_options
                    else None
                ),
            },
        }

    def fetch_model_options(self) -> List[str]:
        api_key = getenv("OPENAI_API_KEY")
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json().get("data", [])
            return [model["id"] for model in data]
        except requests.exceptions.RequestException:
            return []
        except ValueError:
            return []

    def _get_fields(self, chatter_class):
        chatter_fields = {
            OpenAIChatter: {
                "open_ai_model": self.base_field_definitions["open_ai_model"],
                "temperature": self.base_field_definitions["temperature"],
            },
            GroqChatter: {
                "groq_model": self.base_field_definitions["groq_model"],
                "temperature": self.base_field_definitions["temperature"],
            },
        }
        return chatter_fields.get(chatter_class, {})

    def _validations(self, chatter_class):
        validations = []
        fields = self._get_fields(chatter_class)
        if "temperature" in fields:
            validations.extend(
                [
                    {
                        "rule": ("temperature", "ge", self.MIN_TEMPERATURE),
                        "message": f"Temperature must be at least {self.MIN_TEMPERATURE}.",
                    },
                    {
                        "rule": ("temperature", "le", self.MAX_TEMPERATURE),
                        "message": f"Temperature must not exceed {self.MAX_TEMPERATURE}.",
                    },
                ]
            )
        return validations

    @classmethod
    def _constants(cls, chatter_class):
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }

    @property
    def chatter_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "class": cls,
                "fields": self._get_fields(cls),
                "validations": self._validations(cls),
                "constants": self._constants(cls),
            }
            for name, cls in self.chatter_classes.items()
        }
