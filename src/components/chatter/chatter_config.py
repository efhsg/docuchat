from datetime import datetime, timedelta
import json
import os
from typing import Any, Dict, List
import pytz
import requests
from components.chatter.interfaces.chatter_repository import ChatterRepository
from utils.env_utils import getenv
from components.chatter.openai_chatter import OpenAIChatter
from components.chatter.groq_chatter import GroqChatter
from logging import Logger as StandardLogger
from components.database.models import ModelSource


class ModelOptionsFetchError(Exception):
    pass


class ChatterConfig:
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 1.0
    MIN_MAX_TOKENS = 1
    MAX_MAX_TOKENS = 4096
    MIN_TOP_P = 0.0
    MAX_TOP_P = 1.0
    OPEN_API_MODEL_DEFAULT = getenv("OPEN_API_MODEL_DEFAULT", "gpt-4")
    GROQ_API_MODEL_DEFAULT = getenv("GROQ_API_MODEL_DEFAULT", "llama2-70b-4096")
    GROQ_MODELS_API_URL = "https://api.groq.com/openai/v1/models"
    OPENAI_MODELS_API_URL = "https://api.openai.com/v1/models"
    chatter_classes = {
        ModelSource.OpenAI.value: {
            "class": OpenAIChatter,
        },
        ModelSource.Groq.value: {
            "class": GroqChatter,
        },
    }

    def __init__(
        self,
        model_cache_repository: ChatterRepository,
        logger: StandardLogger = None,
    ):
        self.logger = logger
        self.model_cache_repository = model_cache_repository
        self.openai_model_options = self._fetch_openai_model_options()
        self.groq_model_options = self._fetch_groq_model_options()
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
                "options": self.openai_model_options,
                "default": (
                    self.OPEN_API_MODEL_DEFAULT
                    if self.OPEN_API_MODEL_DEFAULT in self.openai_model_options
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
            "max_tokens": {
                "label": "Max Tokens",
                "type": "number",
                "default": 1024,
            },
            "top_p": {
                "label": "Top P",
                "type": "number",
                "default": 1.0,
            },
            "stream": {
                "label": "Stream",
                "type": "boolean",
                "default": True,
            },
            "stop": {
                "label": "Stop Sequence",
                "type": "text",
                "default": None,
            },
        }

    def _get_fields(self, chatter_class):
        field_keys = {
            OpenAIChatter: [
                "open_ai_model",
                "temperature",
                "max_tokens",
                "top_p",
                "stream",
                "stop",
            ],
            GroqChatter: [
                "groq_model",
                "temperature",
                "max_tokens",
                "top_p",
                "stream",
                "stop",
            ],
        }.get(chatter_class, [])
        return {key: self.base_field_definitions[key] for key in field_keys}

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
        if "max_tokens" in fields:
            validations.extend(
                [
                    {
                        "rule": ("max_tokens", "ge", self.MIN_MAX_TOKENS),
                        "message": f"Max tokens must be at least {self.MIN_MAX_TOKENS}.",
                    },
                    {
                        "rule": ("max_tokens", "le", self.MAX_MAX_TOKENS),
                        "message": f"Max tokens must not exceed {self.MAX_MAX_TOKENS}.",
                    },
                ]
            )
        if "top_p" in fields:
            validations.extend(
                [
                    {
                        "rule": ("top_p", "ge", self.MIN_TOP_P),
                        "message": f"Top P must be at least {self.MIN_TOP_P}.",
                    },
                    {
                        "rule": ("top_p", "le", self.MAX_TOP_P),
                        "message": f"Top P must not exceed {self.MAX_TOP_P}.",
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
                "class": class_info["class"],
                "fields": self._get_fields(class_info["class"]),
                "validations": self._validations(class_info["class"]),
                "constants": self._constants(class_info["class"]),
            }
            for name, class_info in self.chatter_classes.items()
        }

    def _fetch_model_options_from_api(
        self, api_url: str, api_key: str, source: ModelSource, enrichment_filename: str
    ) -> List[str]:
        cached_models = self.model_cache_repository.list_model_caches_by_source(source)

        if cached_models and all(
            datetime.now(pytz.utc) - model.updated_at.replace(tzinfo=pytz.utc)
            < timedelta(days=1)
            for model in cached_models
        ):
            return [model.model_id for model in cached_models]

        if not api_key:
            return []

        enrichment_data = self._load_enrichment_data(enrichment_filename)
        enrichment_map = {item["id"]: item for item in enrichment_data}

        try:
            response = requests.get(
                api_url, headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            data = response.json().get("data", [])
            fetched_model_ids = {model["id"] for model in data}

            for model in data:
                model_id = model["id"]
                if model_id in enrichment_map:
                    model.update(enrichment_map[model_id])
                self.model_cache_repository.save_model_cache(source, model_id, model)

            dropped_models = {
                model.model_id for model in cached_models
            } - fetched_model_ids
            for model_id in dropped_models:
                self.model_cache_repository.delete_model_cache(source, model_id)

            return list(fetched_model_ids)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to {api_url} API failed: {e}")
        except ValueError as e:
            self.logger.error(f"Error processing {api_url} API response: {e}")

        return [model.model_id for model in cached_models]

    def _fetch_groq_model_options(self) -> List[str]:
        api_key = getenv("GROQ_API_KEY")
        return self._fetch_model_options_from_api(
            self.GROQ_MODELS_API_URL,
            api_key,
            ModelSource.Groq,
            "enrichments/groq_models_enrichment.json",
        )

    def _fetch_openai_model_options(self) -> List[str]:
        api_key = getenv("OPENAI_API_KEY")
        return self._fetch_model_options_from_api(
            self.OPENAI_MODELS_API_URL,
            api_key,
            ModelSource.OpenAI,
            "enrichments/openai_models_enrichment.json",
        )

    def _load_enrichment_data(self, filename: str):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        try:
            with open(filepath, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            self.logger.error(f"Failed to load enrichment data from {filename}: {e}")
            return []
