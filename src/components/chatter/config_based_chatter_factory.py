import json
from components.chatter.interfaces.chatter import Chatter
from components.chatter.chatter_config import ChatterConfig
from logging import Logger as StandardLogger

from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.models import ModelSource
from .interfaces.chatter_factory import ChatterFactory


class ConfigBasedChatterFactory(ChatterFactory):
    def __init__(
        self,
        logger: StandardLogger = None,
        chatter_repository: ChatterRepository = None,
    ):
        self.logger = logger
        self.chatter_repository = chatter_repository

    def create_chatter(self, method: str, **kwargs) -> Chatter:
        if not method:
            raise ValueError("Chatter method must be specified.")

        chatter_config = ChatterConfig.chatter_classes.get(method)
        if not chatter_config:
            error_msg = f"Chatter method '{method}' is not supported."
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            chatter_class = chatter_config["class"]
            chat_text_processor = chatter_config.get("chat_text_processor")
            model = next((v for k, v in kwargs.items() if k.endswith("_model")), None)

            additional_params = {}
            if method == ModelSource.Groq.value and self.chatter_repository:
                additional_params = self.groq_additional_parameters(model)

            return chatter_class(
                logger=self.logger,
                chatter_repository=self.chatter_repository,
                chat_text_processor=chat_text_processor,
                **kwargs,
                **additional_params,
            )
        except Exception as e:
            if self.logger:
                self.logger.exception("Failed to create chatter: " + str(e))
            raise

    def groq_additional_parameters(self, model) -> dict:
        additional_params = {}
        try:
            model_cache = self.chatter_repository.read_model_cache(
                ModelSource.Groq, model
            )
            huggingface_identifier = model_cache.attributes.get(
                "huggingface_identifier"
            )
            context_window = model_cache.attributes.get("context_window")
            if huggingface_identifier is not None:
                additional_params["huggingface_identifier"] = huggingface_identifier
            if context_window is not None:
                additional_params["context_window"] = context_window
        except Exception as e:
            log_msg = f"Failed to read model cache for {model} due to: {str(e)}"
            if self.logger:
                self.logger.error(log_msg)
            raise
        finally:
            return additional_params
