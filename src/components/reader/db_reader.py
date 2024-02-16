from config import Config
from components.database.connection import Connection
from components.reader.text_compression import TextCompression
from components.logger.logger import Logger
from sqlalchemy.orm.exc import NoResultFound
from components.logger.logger import Logger
from components.reader.text_compression import TextCompression
from components.database.models import ExtractedText, Domain


class DBReader:

    logger = Logger.get_logger()

    def __init__(self, config=None, session=None, compression_service=None):
        self.config = config or Config()
        self.session = session or Connection().create_session()
        self.compression_service = compression_service or TextCompression()

    def save_text(self, text, name, domain_id=None):
        try:
            if domain_id is not None:
                domain_exists = (
                    self.session.query(Domain.id).filter_by(id=domain_id).first()
                )
                if not domain_exists:
                    raise ValueError(f"Domain ID {domain_id} does not exist.")

            compressed_text = self.compression_service.compress(text)
            new_text = ExtractedText(
                name=name,
                text=compressed_text,
                domain_id=domain_id if domain_id else None,
            )
            self.session.add(new_text)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.logger.critical(
                f"Failed to save '{name}' with domain ID '{domain_id}'. Error: {e}"
            )
            raise

    def get_text_by_name(self, name):
        try:
            result = self.session.query(ExtractedText).filter_by(name=name).one()
            return self.compression_service.decompress(result.text)
        except NoResultFound:
            return None

    def get_names_of_texts(self):
        result = self.session.query(ExtractedText.name).all()
        return [name[0] for name in result]

    def name_exists(self, name):
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
            self.session.rollback()
            error_message = f"Failed to delete texts. Error: {e}"
            self.logger.critical(error_message)
            raise
