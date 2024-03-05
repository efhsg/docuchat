from typing import Any, Dict
from components.embedder.sentence_transformer_embedder import (
    SentenceTransformerEmbedder,
)


class EmbedderConfig:
    embedder_classes = {
        "SentenceTransformerEmbedder": SentenceTransformerEmbedder,
    }

    base_field_definitions = {
        "model": {
            "label": "NLP Model",
            "type": "select",
            "default": "all-MiniLM-L6-v2",
            "options": [
                "all-MiniLM-L6-v2",
                "paraphrase-MiniLM-L3-v2",
                "paraphrase-xlm-r-multilingual-v1",
                "stsb-xlm-r-multilingual",
            ],
        },
    }

    @classmethod
    def _get_fields(cls, embedder_class):
        embedder_fields = {
            SentenceTransformerEmbedder: cls.base_field_definitions,
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
