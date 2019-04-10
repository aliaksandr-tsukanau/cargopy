from abc import ABC, abstractmethod
from typing import Mapping, Any, Callable

import marshmallow
from attr import attrs

_no_default = NotImplementedError('No default implementation in base Serializer class')


class Serializer(ABC):
    """
    Abstract base class for Serializer.
    Provides :meth:`serialize` method
    which should be implemented by subclasses.
    """

    @abstractmethod
    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        raise _no_default

    @classmethod
    def from_function(cls, func: Callable[[Mapping[str, Any]], Any]):
        def serialize(self, message: Any) -> Mapping[str, Any]:
            return func(message)

        constructed_type = type(
            '__GeneratedSerializer', (Serializer,), {'serialize': serialize}
        )
        return constructed_type()


@attrs(auto_attribs=True, frozen=True)
class SerializerWithSchema(Serializer, ABC):

    schema: marshmallow.Schema
