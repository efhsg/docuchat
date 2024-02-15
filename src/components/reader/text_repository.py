from components.reader.db_reader import DBReader
from components.database.models import ExtractedText, Domain


class TextRepository:
    def __init__(self, db_reader=None):
        self.db_reader = db_reader or DBReader()

    def save_text(self, text, name, domain_id=None):
        """
        Saves extracted text with an optional domain association.
        """
        try:
            if domain_id:
                domain_exists = (
                    self.db_reader.session.query(Domain.id)
                    .filter_by(id=domain_id)
                    .first()
                )
                if not domain_exists:
                    raise ValueError(f"Domain ID {domain_id} does not exist.")
                new_text = ExtractedText(
                    name=name,
                    text=self.db_reader.compression_service.compress(text),
                    domain_id=domain_id,
                )
            else:
                new_text = ExtractedText(
                    name=name, text=self.db_reader.compression_service.compress(text)
                )
            self.db_reader.session.add(new_text)
            self.db_reader.session.commit()
        except Exception as e:
            self.db_reader.logger.critical(f"Failed to save '{name}'. Error: {e}")
            raise

    def list_text_names(self):
        """
        Lists all saved text names.
        """
        return self.db_reader.get_names_of_extracted_texts()

    def text_exists(self, name):
        """
        Checks if a text name already exists.
        """
        return self.db_reader.name_exists(name)

    def delete_texts(self, names):
        """
        Deletes texts in bulk by their names.
        """
        self.db_reader.delete_extracted_texts_bulk(names)
