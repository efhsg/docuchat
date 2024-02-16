from components.reader.db_reader import DBReader


class TextRepository:
    def __init__(self, db_reader=None):
        self.db_reader = db_reader or DBReader()

    def save_text(self, text, name, domain_id=None):
        """
        Saves extracted text with an optional domain association.
        """
        self.db_reader.save_text(text, name, domain_id)

    def list_text_names(self):
        """
        Lists all saved text names.
        """
        return self.db_reader.list_text_names()

    def text_exists(self, name):
        """
        Checks if a text name already exists.
        """
        return self.db_reader.text_exists(name)

    def delete_texts(self, names):
        """
        Deletes texts in bulk by their names.
        """
        self.db_reader.delete_texts(names)
