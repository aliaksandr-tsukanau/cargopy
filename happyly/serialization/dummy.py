import warnings
from typing import Any, Mapping

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
