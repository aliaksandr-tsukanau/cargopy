from typing import Mapping, Any
import json

from attr import attrs
import marshmallow

from happyly.serialization import Deserializer


@attrs(auto_attribs=True, frozen=True)
class JSONDeserializerWithRequestIdRequired(Deserializer):
    """
    Deserializer for Google Pub/Sub messages
    which expects a message of certain schema
    to be written in `message.data`
    as JSON encoded into binary data with utf-8.

    Schema used with this serializer must define
    some field which is used as request id
    (you can specify which one in constructor).

    If `JSONDeserializerWithRequestIdRequired`
    fails to deserialize some message,
    you can use `build_error_result`
    to fetch request id and provide error message.
    """

    schema: marshmallow.Schema
    request_id_field: str = 'request_id'
    status_field: str = 'status'
    error_field: str = 'error'
    _status_error: str = 'ERROR'

    def deserialize(self, message: Any) -> Mapping[str, Any]:
        """
        Loads message attributes from `message.data`,
        expects it to be a JSON which corresponds
        `self.schema` encoded with utf-8.
        """
        data = message.data.decode('utf-8')
        deserialized, _ = self.schema.loads(data)
        return deserialized

    def build_error_result(self, message: Any, error: Exception) -> Mapping[str, Any]:
        """
        Provides a fallback result when `deserialize` fails.
        Returns a dict with attributes:
        * <request id field>
        * <status field>
        * <error field>
        Field names can be specified in constructor.
        If request id cannot be fetched, it is set to an empty string.
        """
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
