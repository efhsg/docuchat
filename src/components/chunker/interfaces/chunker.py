from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union


class Chunker(ABC):

    @abstractmethod
    def chunk(self, text: str) -> List[str]: ...
