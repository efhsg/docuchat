from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any


class Form(ABC):
    @abstractmethod
    def generate_form(
        self,
        form_config: Dict[str, Any],
        form_values: Dict[str, Union[str, int, bool, list]],
        name: str,
        submit_button: str,
    ) -> bool:
        pass

    @abstractmethod
    def validate_form_values(
        self,
        form_values: Dict[str, Any],
        validations: List[Dict[str, Any]],
        constants: Dict[str, Any],
    ) -> bool:
        pass
