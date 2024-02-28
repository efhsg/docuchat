from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from logging import Logger as StandardLogger
from components.reader.interfaces.text_compressor import TextCompressor
from components.database.interfaces.connector import Connector
from .interfaces.reader_repository import ReaderRepository

from components.database.models import ExtractedText, Domain


class SqlalchemyReaderRepository(ReaderRepository):

    def __init__(
        self,
        config=None,
        connector: Connector = None,
        compressor: TextCompressor = None,
        logger: StandardLogger = None,
    ):
        self.config = config

        self.session = connector.get_session()
        self.compressor = compressor
        self.logger = logger

    def create_domain(self, name):
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

    def domain_exists(self, domain_name):
        result = self.session.query(Domain.id).filter_by(name=domain_name).first()
        return result is not None

    def list_texts_by_domain(self, domain_name):
        try:
            domain = self.session.query(Domain).filter_by(name=domain_name).one()
            texts = (
                self.session.query(ExtractedText)
                .filter_by(domain_id=domain.id)
                .order_by(ExtractedText.name)
                .all()
            )
            return texts
        except NoResultFound:
            self.logger.error(f"Domain '{domain_name}' does not exist.")
            return []
        except Exception as e:
            self.logger.error(
                f"Failed to list texts for domain '{domain_name}'. Error: {e}"
            )
            raise

    def save_text(self, domain_name, text_name, text_type, original_name, text):
        try:
            domain_id = self._get_domain_id(domain_name)
            compressed_text = self.compressor.compress(text)

            existing_text = self.get_text_by_name(domain_name, text_name, text_type)

            if existing_text:
                existing_text.text = compressed_text
                existing_text.original_name = original_name
                self.logger.info(
                    f"Updated '{text_name}' with domain name '{domain_name}' and type '{text_type}'."
                )
            else:
                new_text = ExtractedText(
                    name=text_name,
                    type=text_type,
                    original_name=original_name,
                    text=compressed_text,
                    domain_id=domain_id,
                )
                self.session.add(new_text)
                self.logger.info(
                    f"Saved new '{text_name}' with domain name '{domain_name}' and type '{text_type}'."
                )

            self.session.commit()
        except Exception as e:
            self.logger.critical(
                f"Failed to save/update '{text_name}' with domain name '{domain_name}' and type '{text_type}'. Error: {e}"
            )
            self.session.rollback()
            raise

    def get_text_by_name(self, domain_name, text_name, text_type):
        try:
            domain_id = self._get_domain_id(domain_name)
            result = (
                self.session.query(ExtractedText)
                .filter_by(name=text_name, domain_id=domain_id, type=text_type)
                .first()
            )
            return result
        except NoResultFound:
            return None

    def text_exists(self, domain_name, text_name, text_type):
        return self.get_text_by_name(domain_name, text_name, text_type) is not None

    def delete_texts(self, domain_name, texts):
        if not texts:
            return
        try:
            domain_id = self._get_domain_id(domain_name)
            for text_name, text_type in texts:
                self.session.query(ExtractedText).filter(
                    ExtractedText.name == text_name,
                    ExtractedText.domain_id == domain_id,
                    ExtractedText.type == text_type,
                ).delete(synchronize_session="fetch")
            self.session.commit()
            self.logger.info(f"Deleted specified texts from domain '{domain_name}'.")
        except Exception as e:
            self.logger.error(
                f"Failed to delete specified texts from domain '{domain_name}'. Error: {e}"
            )
            self.session.rollback()
            raise

    def move_text(self, source_domain_name, target_domain_name, texts):
        try:
            skipped_texts = []

            source_domain_id = self._get_domain_id(source_domain_name)
            target_domain_id = self._get_domain_id(target_domain_name)

            if source_domain_id == target_domain_id:
                raise ValueError("Source and target domains must be different.")

            for name, type in texts:
                text_to_move = (
                    self.session.query(ExtractedText)
                    .filter(
                        ExtractedText.domain_id == source_domain_id,
                        ExtractedText.name == name,
                        ExtractedText.type == type,
                    )
                    .first()
                )

                if text_to_move:
                    existing_text = (
                        self.session.query(ExtractedText)
                        .filter(
                            ExtractedText.domain_id == target_domain_id,
                            ExtractedText.name == name,
                            ExtractedText.type == type,
                        )
                        .first()
                    )

                    if existing_text:
                        skipped_texts.append((name, type))
                        continue

                    text_to_move.domain_id = target_domain_id
                else:
                    skipped_texts.append((name, type))

            self.session.commit()
            return skipped_texts
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to move texts due to an error: {e}")

    def _get_domain_id(self, domain_name):
        domain = self.session.query(Domain).filter_by(name=domain_name).first()
        if domain:
            domain_id = domain.id
        else:
            raise ValueError(f"Domain name {domain_name} does not exist.")
        return domain_id

    def update_text_name(self, domain_name, old_name, new_name, text_type):
        if old_name == new_name:
            return False

        try:
            domain_id = self._get_domain_id(domain_name)

            text_to_update = (
                self.session.query(ExtractedText)
                .filter_by(name=old_name, domain_id=domain_id, type=text_type)
                .one()
            )

            if self.text_exists(domain_name, new_name, text_type):
                raise ValueError(
                    f"A text with the name '{new_name}' and type '{text_type}' already exists in the domain '{domain_name}'."
                )

            text_to_update.name = new_name
            self.session.commit()
        except NoResultFound:
            raise ValueError(
                f"The text '{old_name}' of type '{text_type}' does not exist in the domain '{domain_name}'."
            )
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to rename text '{old_name}' of type '{text_type}' to '{new_name}'. Error: {e}"
            )
            raise
        return True
