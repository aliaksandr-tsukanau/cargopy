import json
from typing import Any, Mapping

from happyly import Serializer, Deserializer


class JSONSchemalessSerde(Serializer, Deserializer):
    """
    Simple JSON serializer/deserializer
    which doesn't validate for any schema
    """

    def serialize(self, message_attributes: Mapping[str, Any]) -> str:
        return json.dumps(message_attributes)

    def deserialize(self, message: str) -> Mapping[str, Any]:
        return json.loads(message)
