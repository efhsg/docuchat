from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from components.database.models import ExtractedText


class ReaderRepository(ABC):

    @abstractmethod
    def create_domain(self, name: str) -> None:
        pass

    @abstractmethod
    def list_domains(self) -> List[str]:
        pass

    @abstractmethod
    def list_domains_with_extracted_texts(self) -> List[str]:
        pass

    @abstractmethod
    def delete_domain(self, name: str) -> None:
        pass

    @abstractmethod
    def update_domain(self, old_name: str, new_name: str) -> None:
        pass

    @abstractmethod
    def domain_exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def list_texts_by_domain(self, domain_name: str) -> List[ExtractedText]:
        pass

    @abstractmethod
    def list_texts_by_domain_and_embedder(self, domain_name: str, embedder: str) -> List[ExtractedText]:
        pass

    @abstractmethod
    def save_text(
        self,
        domain_name: str,
        text_name: str,
        text_type: str,
        original_name: str,
        text: str,
    ) -> None:
        pass

    @abstractmethod
    def get_text_by_name(
        self, domain_name: str, text_name: str, text_type: str
    ) -> Optional[ExtractedText]:
        pass

    @abstractmethod
    def text_exists(self, domain_name: str, text_name: str, text_type: str) -> bool:
        pass

    @abstractmethod
    def delete_texts(self, domain_name: str, texts: List[Tuple[str, str]]) -> None:
        pass

    @abstractmethod
    def move_text(
        self,
        source_domain_name: str,
        target_domain_name: str,
        texts: List[Tuple[str, str]],
    ) -> None:
        pass

    @abstractmethod
    def update_text_name(
        self, domain_name: str, old_name: str, new_name: str, text_type: str
    ) -> bool:
        pass
