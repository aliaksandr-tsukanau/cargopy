from typing import Mapping, Any
import json

from attr import attrs
import marshmallow

from happyly.serialization import Deserializer


@attrs(auto_attribs=True, frozen=True)
class JSONDeserializerWithRequestIdRequired(Deserializer):
    schema: marshmallow.Schema
    request_id_field: str = 'request_id'
    status_field: str = 'status'
    error_field: str = 'error'
    _status_error: str = 'ERROR'

    def deserialize(self, message: Any) -> Mapping[str, Any]:
        data = message.data.decode('utf-8')
        deserialized, _ = self.schema.loads(data)
        return deserialized

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        attributes = json.loads(message.data)
        try:
            return {
                self.request_id_field: attributes[self.request_id_field],
                self.status_field: self._status_error,
                self.error_field: repr(error),
            }
        except KeyError as e:
            return {
                self.request_id_field: '',
                self.status_field: self._status_error,
                self.error_field: f'{repr(e)}: '
                f'Message contains no {self.request_id_field}',
            }
