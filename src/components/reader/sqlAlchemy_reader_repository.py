from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from logging import Logger as StandardLogger
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
        logger: StandardLogger = None,
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

    def list_domains_with_extracted_texts(self):
        try:
            domains_with_texts = (
                self.session.query(Domain.name)
                .join(ExtractedText, Domain.id == ExtractedText.domain_id)
                .group_by(Domain.name)
                .having(func.count(ExtractedText.id) > 0)
                .all()
            )
            return [domain[0] for domain in domains_with_texts]
        except Exception as e:
            self.logger.error(
                f"Failed to list domains with at least one text. Error: {e}"
            )
            raise

    def delete_domain(self, name):
        if name.lower() == self.config.default_domain_name:
            raise ValueError(
                f"The default domain '{self.config.default_domain_name}' cannot be deleted."
            )
        try:
            self.session.query(Domain).filter_by(name=name).delete()
            self.session.commit()
        except IntegrityError:
            self.logger.error(
                f"Cannot delete domain '{name}' as it still has associated texts."
            )
            self.session.rollback()
            raise ValueError(
                f"Domain '{name}' cannot be deleted as it still contains extracted texts."
            )
        except Exception as e:
            self.logger.error(f"Failed to delete domain '{name}'. Error: {e}")
            self.session.rollback()
            raise ValueError(
                f"An error occurred while deleting domain '{name}'. Please try again."
            )

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

    def list_text_names_by_domain(self, name):
        try:
            domain = self.session.query(Domain).filter_by(name=name).one()
            result = (
                self.session.query(ExtractedText.name)
                .filter_by(domain_id=domain.id)
                .order_by(ExtractedText.name)
                .all()
            )
            return [name[0] for name in result]
        except NoResultFound:
            self.logger.error(f"Domain '{name}' does not exist.")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list texts for domain '{name}'. Error: {e}")
            raise

    def save_text(self, text, name, domain_name):
        try:
            domain_id = None
            if domain_name:
                domain_id = self._get_domain_id(domain_name)
            compressed_text = self.compressor.compress(text)

            if self.text_exists(name, domain_name):
                existing_text = (
                    self.session.query(ExtractedText)
                    .filter_by(name=name, domain_id=domain_id)
                    .first()
                )
                existing_text.text = compressed_text
                self.logger.info(f"Updated '{name}' with domain name '{domain_name}'.")
            else:
                new_text = ExtractedText(
                    name=name, text=compressed_text, domain_id=domain_id
                )
                self.session.add(new_text)
                self.logger.info(
                    f"Saved new '{name}' with domain name '{domain_name}'."
                )

            self.session.commit()
        except Exception as e:
            self.logger.critical(
                f"Failed to save/update '{name}' with domain name '{domain_name}'. Error: {e}"
            )
            self.session.rollback()
            raise

    def get_text_by_name(self, text_name, domain_name):
        try:
            domain_id = self._get_domain_id(domain_name)
            result = (
                self.session.query(ExtractedText)
                .filter_by(name=text_name, domain_id=domain_id)
                .first()
            )
            if result:
                return self.compressor.decompress(result.text)
            else:
                return None
        except NoResultFound:
            return None

    def list_text_names(self):
        result = self.session.query(ExtractedText.name).all()
        return [name[0] for name in result]

    def text_exists(self, name, domain_name):
        try:
            domain_id = self._get_domain_id(domain_name)
            result = (
                self.session.query(ExtractedText.id)
                .filter_by(name=name, domain_id=domain_id)
                .first()
            )
            return result is not None
        except ValueError:
            raise ValueError(f"Domain name {domain_name} does not exist.")
        except Exception as e:
            self.logger.error(
                f"Failed to check existence of text '{name}' in domain '{domain_name}'. Error: {e}"
            )
            raise

    def delete_texts(self, names, domain_name):
        if not names:
            return
        try:
            domain_id = self._get_domain_id(domain_name)
            self.session.query(ExtractedText).filter(
                ExtractedText.name.in_(names), ExtractedText.domain_id == domain_id
            ).delete(synchronize_session="fetch")
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to delete texts. Error: {e}")
            self.session.rollback()
            raise

    def move_text(self, source_domain_name, target_domain_name, text_names):
        try:
            skipped_texts = []

            source_domain_id = self._get_domain_id(source_domain_name)
            target_domain_id = self._get_domain_id(target_domain_name)

            if source_domain_id == target_domain_id:
                raise ValueError("Source and target domains must be different.")

            existing_texts_in_target = self.list_text_names_by_domain(
                target_domain_name
            )

            texts_to_move = (
                self.session.query(ExtractedText)
                .filter(
                    ExtractedText.domain_id == source_domain_id,
                    ExtractedText.name.in_(text_names),
                )
                .all()
            )

            for text in texts_to_move:
                if text.name in existing_texts_in_target:
                    skipped_texts.append(text.name)
                    continue
                text.domain_id = target_domain_id

            self.session.commit()

            if skipped_texts:
                self.logger.info(
                    f"Skipped moving texts that already exist in the target domain: {skipped_texts}"
                )

            self.logger.info(
                f"Moved texts from domain '{source_domain_name}' to '{target_domain_name}', except for skipped texts."
            )
            return skipped_texts
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to move texts from '{source_domain_name}' to '{target_domain_name}'. Error: {e}"
            )
            raise ValueError(f"Failed to move texts due to an error: {e}")

    def _get_domain_id(self, domain_name):
        domain = self.session.query(Domain).filter_by(name=domain_name).first()
        if domain:
            domain_id = domain.id
        else:
            raise ValueError(f"Domain name {domain_name} does not exist.")
        return domain_id

    def update_text_name(self, old_name, new_name, domain_name) -> bool:
        if old_name == new_name:
            return False

        try:
            domain_id = self._get_domain_id(domain_name)
            text_to_update = (
                self.session.query(ExtractedText)
                .filter_by(name=old_name, domain_id=domain_id)
                .one()
            )
            if self.text_exists(new_name, domain_name):
                raise ValueError(
                    f"A text with the name '{new_name}' already exists in the domain '{domain_name}'."
                )

            text_to_update.name = new_name
            self.session.commit()
        except NoResultFound:
            raise ValueError(
                f"The text '{old_name}' does not exist in the domain '{domain_name}'."
            )
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to rename text '{old_name}' to '{new_name}'. Error: {e}"
            )
            raise
        return True
