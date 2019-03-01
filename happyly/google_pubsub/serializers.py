from typing import Mapping, Any

import marshmallow
from attr import attrs

from happyly.serialization.serializer import Serializer


@attrs(auto_attribs=True, frozen=True)
class BinaryJSONSerializer(Serializer):

    schema: marshmallow.Schema

    def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
        data, _ = self.schema.dumps(message_attributes)
        return data.encode('utf-8')
