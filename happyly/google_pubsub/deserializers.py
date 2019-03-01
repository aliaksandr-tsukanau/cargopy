from typing import Mapping, Any
import json

from attr import attrs
import marshmallow

from happyly.serialization import Deserializer


@attrs(auto_attribs=True, frozen=True)
class JSONDeserializerWithRequestIdRequired(Deserializer):
    schema: marshmallow.Schema
    _request_id_field: str = 'request_id'
    _status_field: str = 'status'
    _error_field: str = 'error'
    _status_error: str = 'ERROR'

    def deserialize(self, message: Any) -> Mapping[str, Any]:
        data = message.data.decode('utf-8')
        deserialized, _ = self.schema.loads(data)
        return deserialized

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        attributes = json.load(message.data)
        try:
            return {
                self._request_id_field: attributes[self._request_id_field],
                self._status_field: self._status_error,
                self._error_field: repr(error),
            }
        except AttributeError:
            raise ValueError(f'message {message} contains no {self._request_id_field}')
