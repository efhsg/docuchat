from typing import Any, Dict
from components.chatter.gpt4_chatter import GPT4Chatter
from utils.env_utils import getenv


class ChatterConfig:
    MIN_TEMPERATURE: float = 0.0
    MAX_TEMPERATURE: float = 1.0

    chatter_classes = {
        "GPT4": GPT4Chatter,
    }

    base_field_definitions = {
        "temperature": {
            "label": "Response Generation Temperature",
            "type": "number",
            "default": float(getenv("CHATTER_TEMPERATURE_DEFAULT", "0.7")),
            "options": [],
        },
    }

    @classmethod
    def _get_fields(cls, chatter_class):
        chatter_fields = {
            GPT4Chatter: cls.base_field_definitions,
        }
        return chatter_fields.get(chatter_class, {})

    @classmethod
    def _validations(cls, chatter_class):
        validations = []
        fields = cls._get_fields(chatter_class)
        if "temperature" in fields:
            validations.extend(
                [
                    {
                        "rule": ("temperature", "ge", cls.MIN_TEMPERATURE),
                        "message": f"Temperature must be at least {cls.MIN_TEMPERATURE}.",
                    },
                    {
                        "rule": ("temperature", "le", cls.MAX_TEMPERATURE),
                        "message": f"Temperature must not exceed {cls.MAX_TEMPERATURE}.",
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
