from typing import Any, Dict, List
import requests
from utils.env_utils import getenv
from components.chatter.open_ai_chatter import OpenAIChatter
from logging import Logger as StandardLogger


class ModelOptionsFetchError(Exception):
    pass


class ChatterConfig:
    MIN_TEMPERATURE: float = 0.0
    MAX_TEMPERATURE: float = 1.0

    def __init__(self, logger: StandardLogger = None):
        self.logger = logger
        self.model_options = self.fetch_model_options()
        self.base_field_definitions = {
            "temperature": {
                "label": "Response Generation Temperature",
                "type": "number",
                "default": float(getenv("CHATTER_TEMPERATURE_DEFAULT", "0.7")),
                "options": [],
            },
            "model": {
                "label": "Model",
                "type": "select",
                "options": self.model_options,
                "default": self.model_options[0] if self.model_options else None,
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

    chatter_classes = {
        "OpenAI": OpenAIChatter,
    }

    def _get_fields(self, chatter_class):
        chatter_fields = {
            OpenAIChatter: self.base_field_definitions,
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
