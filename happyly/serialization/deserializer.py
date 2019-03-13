from abc import ABC, abstractmethod
from typing import Mapping, Any


_not_impl = NotImplementedError('No default implementation in base Deserializer class')


class Deserializer(ABC):
    @abstractmethod
    def deserialize(self, message: Any) -> Mapping[str, Any]:
        raise _not_impl

    @abstractmethod
    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        raise _not_impl
