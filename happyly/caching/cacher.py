from abc import ABC, abstractmethod
from typing import Any

_no_default_impl = NotImplementedError('No default implementation for class Cacher')


class Cacher(ABC):
    @abstractmethod
    def add(self, message: Any, key: str):
        raise _no_default_impl

    @abstractmethod
    def remove(self, key: str):
        raise _no_default_impl

    @abstractmethod
    def get(self, key: str):
        raise _no_default_impl
