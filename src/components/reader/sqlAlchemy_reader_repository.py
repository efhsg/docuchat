from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from components.logger.interfaces.logger import Logger
from components.reader.interfaces.text_compressor import TextCompressor
from components.database.interfaces.connector import Connector
from .interfaces.reader_repository import ReaderRepository

from config import Config
from components.database.models import ExtractedText, Domain


class SqlalchemyReaderRepository(ReaderRepository):

    def __init__(
        self,
        config=None,
        connector: Connector = None,
        compressor: TextCompressor = None,
        logger: Logger = None,
    ):
        self.config = config or Config()

        self.session = connector.get_session()
        self.compressor = compressor
        self.logger = logger
        self.default_domain_name = self.config.default_domain_name

    def create_domain(self, name):
        if name.lower() == self.default_domain_name.lower():
            raise ValueError(
                f"Cannot create domain with default name '{self.default_domain_name}'."
            )
        if self.domain_exists(name):
            raise ValueError(f"Domain with name '{name}' already exists.")
        try:
            new_domain = Domain(name=name)
            self.session.add(new_domain)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Failed to create domain. Error: {e}")
            raise ValueError(f"Error creating domain: '{e}'")

    def list_domains(self):
        try:
            return [domain[0] for domain in self.session.query(Domain.name).all()]
        except Exception as e:
            self.logger.error(f"Failed to list domains. Error: {e}")
            raise

    def list_domains_without_default(self):
        try:
            domains = (
                self.session.query(Domain.name)
                .filter(func.lower(Domain.name) != func.lower(self.default_domain_name))
                .all()
            )
            return [domain[0] for domain in domains]
        except Exception as e:
            self.logger.error(f"Failed to list domains without default. Error: {e}")
            raise

    def delete_domain(self, name):
        if name.lower() == self.config.default_domain_name:
            raise ValueError(
                f"The default domain '{self.config.default_domain_name}' domain cannot be deleted."
            )
        try:
            self.session.query(Domain).filter_by(name=name).delete()
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to delete domain '{name}'. Error: {e}")
            self.session.rollback()
            raise ValueError(f"Failed to delete domain '{name}'. Error: {e}")

    def update_domain(self, old_name, new_name):
        if old_name.lower() == self.config.default_domain_name:
            raise ValueError(
                f"The '{self.config.default_domain_name}' domain cannot be updated."
            )
        if self.domain_exists(new_name):
            raise ValueError(f"The domain '{new_name}' already exists.")
        try:
            domain = self.session.query(Domain).filter_by(name=old_name).first()
            if domain:
                domain.name = new_name
                self.session.commit()
            else:
                raise ValueError(f"Domain with name '{old_name}' does not exist.")
        except Exception as e:
            self.logger.error(f"Failed to update domain '{old_name}'. Error: {e}")
            self.session.rollback()
            raise ValueError(f"Failed to update domain '{old_name}'. Error: {e}")

    def domain_exists(self, name):
        result = self.session.query(Domain.id).filter_by(name=name).first()
        return result is not None

    def save_text(self, text, name, domain_id=None):
        try:
            if domain_id is not None:
                domain_exists = (
                    self.session.query(Domain.id).filter_by(id=domain_id).first()
                )
                if not domain_exists:
                    raise ValueError(f"Domain ID {domain_id} does not exist.")

            compressed_text = self.compressor.compress(text)
            new_text = ExtractedText(
                name=name,
                text=compressed_text,
                domain_id=domain_id if domain_id else None,
            )
            self.session.add(new_text)
            self.session.commit()
        except Exception as e:
            self.logger.critical(
                f"Failed to save '{name}' with domain ID '{domain_id}'. Error: {e}"
            )
            self.session.rollback()
            raise

    def get_text_by_name(self, name):
        try:
            result = self.session.query(ExtractedText).filter_by(name=name).one()
            return self.compressor.decompress(result.text)
        except NoResultFound:
            return None

    def list_text_names(self):
        result = self.session.query(ExtractedText.name).all()
        return [name[0] for name in result]

    def text_exists(self, name):
        result = self.session.query(ExtractedText.id).filter_by(name=name).first()
        return result is not None

    def delete_texts(self, names):
        if not names:
            return
        try:
            self.session.query(ExtractedText).filter(
                ExtractedText.name.in_(names)
            ).delete(synchronize_session="fetch")
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to delete texts. Error: {e}")
            self.session.rollback()
            raise
