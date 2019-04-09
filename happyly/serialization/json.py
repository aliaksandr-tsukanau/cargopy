import json
from typing import Any, Mapping

from attr import attrs

from happyly import Serializer, Deserializer
from .deserializer import DeserializerWithSchema
from .serializer import SerializerWithSchema


class JSONSchemalessSerde(Serializer, Deserializer):
    """
    Simple JSON serializer/deserializer
    which doesn't validate for any schema
    """

    def serialize(self, message_attributes: Mapping[str, Any]) -> str:
        return json.dumps(message_attributes)

    def deserialize(self, message: str) -> Mapping[str, Any]:
        return json.loads(message)


@attrs(auto_attribs=True)
class JSONSerializerForSchema(SerializerWithSchema):
    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        data, _ = self.schema.dumps(message_attributes)
        return data


@attrs(auto_attribs=True)
class JSONDeserializerForSchema(DeserializerWithSchema):
    def deserialize(self, message: Any) -> Mapping[str, Any]:
        deserialized, _ = self.schema.loads(message)
        return deserialized


@attrs(auto_attribs=True)
class BinaryJSONSerializerForSchema(SerializerWithSchema):
    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        data, _ = self.schema.dumps(message_attributes)
        return data.encode('utf-8')


@attrs(auto_attribs=True)
class BinaryJSONDeserialierForSchema(DeserializerWithSchema):
    def deserialize(self, message: Any) -> Mapping[str, Any]:
        data = message.data.decode('utf-8')
        deserialized, _ = self.schema.loads(data)
        return deserialized
