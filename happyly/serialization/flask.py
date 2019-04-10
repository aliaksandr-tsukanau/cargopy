from typing import Mapping, Any

from attr import attrs

from happyly.serialization.serializer import SerializerWithSchema
from happyly.serialization import DummyValidator


@attrs(auto_attribs=True)
class JsonifyForSchema(SerializerWithSchema):
    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        DummyValidator(schema=self.schema).serialize(message_attributes)
        # raises error is msg doesn't match schema

        import flask

        return flask.jsonify(message_attributes)
