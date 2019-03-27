from abc import ABC, abstractmethod


_not_impl = NotImplementedError('No default implementation in base logger class')


class BaseLogger(ABC):
    @abstractmethod
    def info(self, message: str):
        raise _not_impl

    @abstractmethod
    def debug(self, message: str):
        raise _not_impl

    @abstractmethod
    def warning(self, message: str):
        raise _not_impl

    @abstractmethod
    def exception(self, message: str):
        raise _not_impl

    @abstractmethod
    def error(self, message: str):
        raise _not_impl
