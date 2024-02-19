from abc import ABC, abstractmethod
from logging import Logger as StandardLogger


class Logger(ABC):

    @staticmethod
    @abstractmethod
    def get_logger(name: str = "default") -> StandardLogger:
        pass
