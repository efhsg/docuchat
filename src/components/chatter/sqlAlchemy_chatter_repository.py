from sqlalchemy.orm.exc import NoResultFound
from typing import List, Optional
from logging import Logger as StandardLogger
from components.chatter.interfaces.chatter_repository import ChatterRepository
from components.database.interfaces.connector import Connector
from components.database.models import ModelCache, ModelSource
from sqlalchemy.orm.attributes import flag_modified


class SqlalchemyChatterRepository(ChatterRepository):

    def __init__(
        self,
        connector: Connector,
        logger: StandardLogger = None,
    ):
        self.session = connector.get_session()
        self.logger = logger

    def save_model_cache(
        self, source: ModelSource, model_id: str, attributes: dict
    ) -> None:
        try:
            cache_entry = (
                self.session.query(ModelCache)
                .filter_by(source=source, model_id=model_id)
                .first()
            )
            if cache_entry:
                cache_entry.attributes = attributes
                flag_modified(cache_entry, "attributes")
                self.logger.info(
                    f"Updated cache for {source.value} model '{model_id}'."
                )
            else:
                new_cache_entry = ModelCache(
                    source=source, model_id=model_id, attributes=attributes
                )
                self.session.add(new_cache_entry)
                self.logger.info(
                    f"Created new cache for {source.value} model '{model_id}'."
                )
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to save cache for {source.value} model '{model_id}'. Error: {e}"
            )
            raise

    def read_model_cache(
        self, source: ModelSource, model_id: str
    ) -> Optional[ModelCache]:
        try:
            return (
                self.session.query(ModelCache)
                .filter_by(source=source, model_id=model_id)
                .one_or_none()
            )
        except NoResultFound:
            return None

    def delete_model_cache(self, source: ModelSource, model_id: str) -> None:
        try:
            result = (
                self.session.query(ModelCache)
                .filter_by(source=source, model_id=model_id)
                .delete()
            )
            self.session.commit()
            if result:
                self.logger.info(
                    f"Deleted cache for {source.value} model '{model_id}'."
                )
            else:
                self.logger.info(
                    f"No cache found for {source.value} model '{model_id}' to delete."
                )
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to delete cache for {source.value} model '{model_id}'. Error: {e}"
            )
            raise

    def list_all_model_caches(self) -> List[ModelCache]:
        try:
            return self.session.query(ModelCache).all()
        except Exception as e:
            self.logger.error("Failed to list all model caches. Error: {e}")
            raise

    def list_model_caches_by_source(self, source: ModelSource) -> List[ModelCache]:
        try:
            return self.session.query(ModelCache).filter_by(source=source).all()
        except Exception as e:
            self.logger.error(
                f"Failed to list model caches for source {source.value}. Error: {e}"
            )
            raise
