from abc import ABC, abstractmethod
from typing import List, Optional
from components.database.models import ModelCache, ModelSource


class ChatterRepository(ABC):

    @abstractmethod
    def save_model_cache(
        self, source: ModelSource, model_id: str, attributes: dict
    ) -> None:
        """
        Inserts a new model cache record or updates an existing one based on the source and model_id.

        :param source: The source of the model (e.g., Groq, OpenAI).
        :param model_id: The unique identifier for the model.
        :param attributes: A dictionary of attributes to store in the cache.
        """
        pass

    @abstractmethod
    def read_model_cache(
        self, source: ModelSource, model_id: str
    ) -> Optional[ModelCache]:
        """
        Retrieves a model cache record by its source and model_id.

        :param source: The source of the model.
        :param model_id: The unique identifier for the model.
        :return: An instance of ModelCache if found, otherwise None.
        """
        pass

    @abstractmethod
    def delete_model_cache(self, source: ModelSource, model_id: str) -> None:
        """
        Deletes a model cache record by its source and model_id.

        :param source: The source of the model.
        :param model_id: The unique identifier for the model.
        """
        pass

    @abstractmethod
    def list_all_model_caches(self) -> List[ModelCache]:
        """
        Lists all model cache records in the database.

        :return: A list of ModelCache instances.
        """
        pass

    @abstractmethod
    def list_model_caches_by_source(self, source: ModelSource) -> List[ModelCache]:
        """
        Lists all model cache records for a specific source.

        :param source: The source of the models to list.
        :return: A list of ModelCache instances from the specified source.
        """
        pass
