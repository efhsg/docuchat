from os import getenv
from components.chatter.groq_chat_text_processor import GroqChatTextProcessor
from components.chatter.interfaces.chatter import Chatter
from components.chatter.chatter_config import ChatterConfig

from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.models import ModelSource
from .interfaces.chatter_factory import ChatterFactory
from components.logger.native_logger import NativeLogger as Logger
from transformers import AutoTokenizer


class ConfigBasedChatterFactory(ChatterFactory):
    def __init__(
        self, logger: Logger = None, chatter_repository: ChatterRepository = None
    ):
        self.logger = logger
        self.chatter_repository = chatter_repository

    def create_chatter(self, method: str, **kwargs) -> Chatter:
        self._validate_method(method)
        chatter_config = self._get_chatter_config(method)
        chatter_class = chatter_config["class"]
        model = self._extract_model_from_kwargs(kwargs)
        additional_params = self._get_additional_params(method, model)

        return chatter_class(
            logger=self.logger,
            **kwargs,
            **additional_params,
        )

    def _validate_method(self, method: str):
        if not method:
            raise ValueError("Chatter method must be specified.")

    def _get_chatter_config(self, method: str):
        chatter_config = ChatterConfig.chatter_classes.get(method)
        if not chatter_config:
            self._log_error(f"Chatter method '{method}' is not supported.")
            raise ValueError(f"Chatter method '{method}' is not supported.")
        return chatter_config

    def _extract_model_from_kwargs(self, kwargs):
        return next((v for k, v in kwargs.items() if k.endswith("_model")), None)

    def _get_additional_params(self, method, model) -> dict:
        if method == ModelSource.Groq.value:
            return self._groq_additional_parameters(model)
        return {}

    def _groq_additional_parameters(self, model) -> dict:
        additional_params = {}
        try:

            model_cache = self.chatter_repository.read_model_cache(
                ModelSource.Groq, model
            )

            additional_params["chat_text_processor"] = GroqChatTextProcessor(
                tokenizer=AutoTokenizer.from_pretrained(
                    pretrained_model_name_or_path=model_cache.attributes.get(
                        "huggingface_identifier"
                    ),
                    token=getenv("HUGGINGFACEHUB_API_TOKEN"),
                ),
                context_window=model_cache.attributes.get("context_window"),
                logger=self.logger,
            )

        except Exception as e:
            log_msg = f"Failed to read model cache for {model} due to: {str(e)}"
            if self.logger:
                self.logger.error(log_msg)
            raise
        finally:
            return additional_params

    def _log_error(self, message: str):
        if self.logger:
            self.logger.error(message)
