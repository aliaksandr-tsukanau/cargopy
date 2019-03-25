import json
from typing import Any, Mapping, Optional

from happyly.caching.cacher import Cacher
from happyly.handling import HandlingResult


class CacheByRequestIdMixin:
    """
    Mixin which adds caching functionality to Listener.
    Utilizes notions of listener's topic
    and request id of message -
    otherwise will not work.

    To be used via multiple inheritance.
    For example, given some component SomeListener
    you can define its caching equivalent
    by defining SomeCachedListener which inherits
    from both SomeListener and CacheByRequestIdMixin.
    """

    def __init__(self, cacher: Cacher):
        self.cacher = cacher

    def on_received(self, message: Any):
        super().on_received(message)

        try:
            req_id = self._get_req_id(message)
        except Exception:
            pass
        else:
            data = json.dumps(
                {'topic': self.from_topic, 'data': json.loads(message.data)}
            )
            self.cacher.add(data, key=req_id)

    def _get_req_id(self, message: Any) -> str:
        assert self.deserializer is not None

        attribtues = self.deserializer.deserialize(message)
        return attribtues[self.deserializer.request_id_field]

    def _rm(self, parsed_message: Mapping[str, Any]):
        assert self.deserializer is not None
        self.cacher.remove(parsed_message[self.deserializer.request_id_field])

    def on_published(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
    ):
        super().on_published(original_message, parsed_message, result)
        if parsed_message is not None:
            self._rm(parsed_message)

    def on_deserialization_failed(self, message: Any, error: Exception):
        super().on_deserialization_failed(message, error)

        try:
            req_id = self._get_req_id(message)
        except Exception:
            pass
        else:
            self.cacher.remove(key=req_id)
