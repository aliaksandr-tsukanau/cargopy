import warnings
from typing import Any, Mapping

import marshmallow
from attr import attrs

from happyly.serialization import Serializer
from .deserializer import Deserializer


class DummySerde(Deserializer, Serializer):
    def _identity_transform(self, message):
        if self is DUMMY_DESERIALIZER:
            warnings.warn(
                "Please use DUMMY_SERDE instead, "
                "DUMMY_DESERIALIZER will be removed in happyly v0.9.0.",
                DeprecationWarning,
                stacklevel=2,
            )
        if isinstance(message, Mapping):
            return message
        elif message is None:
            return {}
        else:
            raise ValueError(
                'Dummy deserializer requires message attributes '
                'in form of dict-like structure as input'
            )

    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        return self._identity_transform(message_attributes)

    def deserialize(self, message) -> Mapping[str, Any]:
        return self._identity_transform(message)


DUMMY_DESERIALIZER: DummySerde = DummySerde()

DUMMY_SERDE: DummySerde = DummySerde()
"""
Serializer/deserializer which transforms message attributes to themselves
"""


@attrs(auto_attribs=True, frozen=True)
class DummyValidator(Deserializer, Serializer):
    """
    Serializer/deserializer which transforms message attributes to themselves
    along with validating against message schema.
    """

    schema: marshmallow.Schema
    """
    Schema which will be used to validate the provided message
    """

    def _validate(self, message):
        errors = self.schema.validate(message)
        if errors != {}:
            raise marshmallow.ValidationError(str(errors))

    def deserialize(self, message: Mapping[str, Any]) -> Mapping[str, Any]:
        self._validate(message)
        return message

    def serialize(self, message_attributes: Mapping[str, Any]) -> Mapping[str, Any]:
        self._validate(message_attributes)
        return message_attributes
