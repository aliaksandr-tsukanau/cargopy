from abc import ABC, abstractmethod
from typing import Mapping, Any


_no_default = NotImplementedError('No default implementation in base Serializer class')


class Serializer(ABC):
    @abstractmethod
    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        raise _no_default
