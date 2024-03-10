from typing import Any, Dict
from components.embedder.sentence_transformer_embedder import (
    SentenceTransformerEmbedder,
)
from utils.env_utils import getenv


class EmbedderConfig:
    embedder_classes = {
        "SentenceTransformerEmbedder": SentenceTransformerEmbedder,
    }

    base_field_definitions = {
        "model": {
            "label": "NLP Model",
            "type": "select",
            "default": getenv("EMBEDDING_NLP_MODEL_DEFAULT", "all-MiniLM-L6-v2"),
            "options": getenv(
                "EMBEDDING_NLP_MODEL_OPTIONS",
                "all-MiniLM-L6-v2,stsb-xlm-r-multilingual",
            ),
        },
    }

    @classmethod
    def _get_fields(cls, embedder_class):
        embedder_fields = {
            SentenceTransformerEmbedder: {
                "model": cls.base_field_definitions["model"],
            },
        }
        return embedder_fields.get(embedder_class, {})

    @classmethod
    def _validations(cls, embedder_class):
        return []

    @classmethod
    def _constants(cls, embedder_class):
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }

    @property
    def embedder_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "class": cls,
                "fields": self._get_fields(cls),
                "validations": self._validations(cls),
                "constants": self._constants(cls),
            }
            for name, cls in self.embedder_classes.items()
        }
