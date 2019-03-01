from abc import ABC
from typing import Mapping, Any


_no_default = NotImplementedError('No default implementation in base Serializer class')


class Serializer(ABC):

    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        raise _no_default

    def build_error_result(self, message_attributes: Mapping[str, Any], error: Exception) -> Any:
        raise _no_default
