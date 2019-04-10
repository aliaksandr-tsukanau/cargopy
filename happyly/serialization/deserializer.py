from abc import ABC, abstractmethod
from typing import Mapping, Any, Callable

import marshmallow
from attr import attrs

_not_impl = NotImplementedError('No default implementation in base Deserializer class')


class Deserializer(ABC):
    @abstractmethod
    def deserialize(self, message: Any) -> Mapping[str, Any]:
        raise _not_impl

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        raise error from error

    @classmethod
    def from_function(cls, func: Callable[[Any], Mapping[str, Any]]):
        def deserialize(self, message: Any) -> Mapping[str, Any]:
            return func(message)

        constructed_type = type(
            '__GeneratedDeserializer', (Deserializer,), {'deserialize': deserialize}
        )
        return constructed_type()


@attrs(auto_attribs=True, frozen=True)
class DeserializerWithSchema(Deserializer, ABC):

    schema: marshmallow.Schema
