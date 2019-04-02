from abc import ABC, abstractmethod
from typing import Any

_no_default_impl = NotImplementedError('No default implementation for class Cacher')


class Cacher(ABC):
    """
    Abstract base class
    which defines interface of any caching component
    to be used via :class:`.CacheByRequestIdMixin` or similar mixin.
    """

    @abstractmethod
    def add(self, data: Any, key: str):
        """
        Add the provided data to cache
        and store it by the provided key.
        """
        raise _no_default_impl

    @abstractmethod
    def remove(self, key: str):
        """
        Remove data from cache
        which is stored by the provided key.
        """
        raise _no_default_impl

    @abstractmethod
    def get(self, key: str):
        """
        Returns data which is stored in cache
        by the provided key.
        """
        raise _no_default_impl
