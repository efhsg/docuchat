from abc import ABC, abstractmethod


class ReaderRepository(ABC):
    """
    Interface for interacting with data in a repository, specifically for reading operations.
    """

    @abstractmethod
    def save_text(self, text, name, domain_id=None):
        """
        Saves extracted text with an optional domain association.
        """
        pass

    @abstractmethod
    def get_text_by_name(self, name):
        """
        Retrieves text by its name.
        """
        pass

    @abstractmethod
    def list_text_names(self):
        """
        Lists all saved text names.
        """
        pass

    @abstractmethod
    def text_exists(self, name):
        """
        Checks if a text with the given name exists in the repository.
        """
        pass

    @abstractmethod
    def delete_texts(self, names):
        """
        Deletes texts in bulk by their names.
        """
        pass
