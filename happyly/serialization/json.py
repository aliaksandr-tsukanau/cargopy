import json
from typing import Any, Mapping

from happyly import Serializer, Deserializer


class JSONSchemalessSerde(Serializer, Deserializer):
    def serialize(self, message_attributes: Mapping[str, Any]) -> str:
        return json.dumps(message_attributes)

    def deserialize(self, message: str) -> Mapping[str, Any]:
        return json.loads(message)
