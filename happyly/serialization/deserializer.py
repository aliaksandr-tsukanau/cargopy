from abc import ABC, abstractmethod
from typing import Mapping, Any

import marshmallow
from attr import attrs

_not_impl = NotImplementedError('No default implementation in base Deserializer class')


class Deserializer(ABC):
    @abstractmethod
    def deserialize(self, message: Any) -> Mapping[str, Any]:
        raise _not_impl

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        raise error from error


@attrs(auto_attribs=True, frozen=True)
class DeserializerWithSchema(Deserializer, ABC):

    schema: marshmallow.Schema
