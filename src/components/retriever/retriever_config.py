from components.retriever.simple_nearest_neighbor_retriever import (
    SimpleNearestNeighborRetriever,
)
from typing import Any, Dict
from utils.env_utils import getenv


class RetrieverConfig:
    retriever_classes = {
        "simple_nearest_neighbor": SimpleNearestNeighborRetriever,
    }

    base_field_definitions = {
        "top_n": {
            "label": "Top N Results",
            "type": "number",
            "default": int(getenv("RETRIEVER_TOP_N_DEFAULT", "5")),
            "options": [],
        },
    }

    @classmethod
    def _get_fields(cls, retriever_class):
        retriever_fields = {
            SimpleNearestNeighborRetriever: cls.base_field_definitions,
        }
        return retriever_fields.get(retriever_class, {})

    @classmethod
    def _validations(cls, retriever_class):
        return []

    @classmethod
    def _constants(cls, retriever_class):
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }

    @property
    def retriever_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "class": cls,
                "fields": self._get_fields(cls),
                "validations": self._validations(cls),
                "constants": self._constants(cls),
            }
            for name, cls in self.retriever_classes.items()
        }
