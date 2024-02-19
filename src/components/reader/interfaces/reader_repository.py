from abc import ABC, abstractmethod


class ReaderRepository(ABC):

    @abstractmethod
    def create_domain(self, name):
        pass

    @abstractmethod
    def list_domains(self):
        pass

    @abstractmethod
    def list_domains_without_default(self):
        pass

    @abstractmethod
    def delete_domain(self, name):
        pass

    @abstractmethod
    def update_domain(self, old_name, new_name):
        pass

    @abstractmethod
    def domain_exists(self, name):
        pass

    @abstractmethod
    def list_text_names_by_domain(self, name):
        pass

    @abstractmethod
    def save_text(self, text, name, domain_name=None):
        pass

    @abstractmethod
    def get_text_by_name(self, name):
        pass

    @abstractmethod
    def list_text_names(self):
        pass

    @abstractmethod
    def text_exists(self, name):
        pass

    @abstractmethod
    def delete_texts(self, names):
        pass
