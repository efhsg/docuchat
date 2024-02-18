from sqlalchemy import func
from .interfaces.reader_repository import ReaderRepository
from sqlalchemy.exc import IntegrityError
from config import Config
from components.database.connector import Connector
from sqlalchemy.orm.exc import NoResultFound
from components.logger.logger import Logger
from components.database.models import ExtractedText, Domain


class SqlalchemyReaderRepository(ReaderRepository):

    def __init__(self, config=None, session=None, compressor=None, logger=None):
        self.config = config or Config()
        self.session = session or Connector().create_session()
        self.compressor = compressor
        self.logger = logger or Logger.get_logger()
        self.default_domain_name = self.config.default_domain_name

    def create_domain(self, name):
        if name.lower() == self.default_domain_name.lower():
            raise ValueError(
                f"Cannot create domain with default name '{self.default_domain_name}'."
            )
        with self.session.begin():
            try:
                new_domain = Domain(name=name)
                self.session.add(new_domain)
            except IntegrityError:
                raise ValueError(f"Domain with name '{name}' already exists.")

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
        with self.session.begin():
            try:
                self.session.query(Domain).filter_by(name=name).delete()
            except Exception as e:
                self.logger.error(f"Failed to delete domain '{name}'. Error: {e}")
                raise ValueError(f"Failed to delete domain '{name}'. Error: {e}")

    def update_domain(self, old_name, new_name):
        if old_name.lower() == self.config.default_domain_name:
            raise ValueError(
                f"The '{self.config.default_domain_name}' domain cannot be updated."
            )
        if self.domain_exists(new_name):
            raise ValueError(f"Can't update. The domain '{new_name}' already exists.")
        with self.session.begin():
            try:
                domain = self.session.query(Domain).filter_by(name=old_name).first()
                if domain:
                    domain.name = new_name
                else:
                    raise ValueError(f"Domain with name '{old_name}' does not exist.")
            except Exception as e:
                self.logger.error(f"Failed to update domain '{old_name}'. Error: {e}")
                raise ValueError(f"Failed to update domain '{old_name}'. Error: {e}")

    def domain_exists(self, name):
        result = self.session.query(Domain.id).filter_by(name=name).first()
        return result is not None

    def save_text(self, text, name, domain_id=None):
        with self.session.begin():
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
            except Exception as e:
                self.logger.critical(
                    f"Failed to save '{name}' with domain ID '{domain_id}'. Error: {e}"
                )
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
        with self.session.begin():
            try:
                self.session.query(ExtractedText).filter(
                    ExtractedText.name.in_(names)
                ).delete(synchronize_session="fetch")
            except Exception as e:
                error_message = f"Failed to delete texts. Error: {e}"
                self.logger.critical(error_message)
                raise
