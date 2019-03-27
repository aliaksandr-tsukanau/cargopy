from typing import Any, Mapping

from .deserializer import Deserializer


class DummyDeserializer(Deserializer):
    def deserialize(self, message) -> Mapping[str, Any]:
        if isinstance(message, Mapping):
            return message
        else:
            raise ValueError(
                'Dummy deserializer requires message attributes '
                'in form of dict-like structure as input'
            )

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        raise error


DUMMY_DESERIALIZER = DummyDeserializer()
