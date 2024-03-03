from typing import Dict, Any, Tuple, Union
from components.chunker.interfaces.chunker import Chunker
from utils.env_utils import getenv

from .semantic_chunker import SemanticChunker
from .fixed_length_overlap_chunker import FixedLengthOverLapChunker
from .fixed_length_chunker import FixedLengthChunker
from .recursive_split_chunker import RecursiveSplitChunker


from typing import List, Dict, Any
from .interfaces.chunker import Chunker


class ChunkerConfig:
    MIN_CHUNK_SIZE: int = 1
    MAX_CHUNK_SIZE: int = 100000
    MIN_OVERLAP_SIZE: int = 0

    chunker_classes: Dict[str, Chunker] = {
        "Fixed-Length": FixedLengthChunker,
        "Fixed-Length Overlap": FixedLengthOverLapChunker,
        "Recursive Split": RecursiveSplitChunker,
        "Semantic": SemanticChunker,
    }

    base_field_definitions = {
        "chunk_size": {"label": "Chunk Size", "type": "number", "default": 2000},
        "overlap_size": {"label": "Overlap Size", "type": "number", "default": 100},
        "separators": {
            "label": "Separators",
            "type": "multi_select",
            "default": ["\n\n", "\n", " ", ""],
            "options": ["\n\n", "\n", "\r", " ", "", ".", "!", "?", ",", ";", ":", "|"],
        },
        "model": {
            "label": "NLP Model",
            "type": "select",
            "default": getenv("CHUNKER_NLP_MODEL_DEFAULT", "en_core_web_sm"),
            "options": getenv(
                "CHUNKER_NLP_MODEL_OPTIONS",
                "en_core_web_sm,en_core_web_md,en_core_web_lg",
            ),
        },
        "max_chunk_size": {
            "label": "Max Chunk Size",
            "type": "number",
            "default": 2000,
        },
    }

    @classmethod
    def _get_fields(cls, chunker_class):
        chunker_fields = {
            FixedLengthChunker: {
                "chunk_size": cls.base_field_definitions["chunk_size"]
            },
            FixedLengthOverLapChunker: {
                "chunk_size": cls.base_field_definitions["chunk_size"],
                "overlap_size": cls.base_field_definitions["overlap_size"],
            },
            RecursiveSplitChunker: {
                "chunk_size": cls.base_field_definitions["chunk_size"],
                "overlap_size": {
                    **cls.base_field_definitions["overlap_size"],
                    "default": 200,
                },
                "separators": cls.base_field_definitions["separators"],
            },
            SemanticChunker: {
                "model": cls.base_field_definitions["model"],
                "max_chunk_size": cls.base_field_definitions["max_chunk_size"],
            },
        }

        return chunker_fields.get(chunker_class, {})

    @classmethod
    def _validations(
        cls, chunker_class
    ) -> List[Dict[str, Union[Tuple[str, str, int], str]]]:
        validations = []
        fields = cls._get_fields(chunker_class)
        if "chunk_size" in fields:
            validations.extend(
                [
                    {
                        "rule": ("chunk_size", "ge", cls.MIN_CHUNK_SIZE),
                        "message": f"Chunk size must be at least {cls.MIN_CHUNK_SIZE}.",
                    },
                    {
                        "rule": ("chunk_size", "le", cls.MAX_CHUNK_SIZE),
                        "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
                    },
                ]
            )
        if "overlap_size" in fields:
            validations.extend(
                [
                    {
                        "rule": ("overlap_size", "ge", cls.MIN_OVERLAP_SIZE),
                        "message": f"Overlap size must be at least {cls.MIN_OVERLAP_SIZE}.",
                    },
                    {
                        "rule": ("overlap_size", "lt", "chunk_size"),
                        "message": "Overlap size must be less than Chunk size.",
                    },
                ]
            )
        if "max_chunk_size" in fields:
            validations.extend(
                [
                    {
                        "rule": ("max_chunk_size", "ge", cls.MIN_CHUNK_SIZE),
                        "message": f"Chunk size must be at least {cls.MIN_CHUNK_SIZE}.",
                    },
                    {
                        "rule": ("max_chunk_size", "le", cls.MAX_CHUNK_SIZE),
                        "message": f"Chunk size must not exceed {cls.MAX_CHUNK_SIZE}.",
                    },
                ]
            )
        return validations

    @classmethod
    def _constants(cls, chunker_class) -> Dict[str, int]:
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and attr.isupper()
            and not attr.startswith("_")
        }

    @property
    def chunker_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "class": cls,
                "fields": self._get_fields(cls),
                "validations": self._validations(cls),
                "constants": self._constants(cls),
            }
            for name, cls in self.chunker_classes.items()
        }
