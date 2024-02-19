from abc import ABC, abstractmethod
from pymysql.connections import Connection
from sqlalchemy.orm import Session


class Connector(ABC):

    @abstractmethod
    def get_connection(self) -> Connection:
        pass

    @abstractmethod
    def get_session(self) -> Session:
        pass
