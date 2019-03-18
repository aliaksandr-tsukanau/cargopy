from typing import Mapping, Any

from happyly.handling.handler import Handler


class _DummyHandler(Handler):
    def handle(self, message: Mapping[str, Any]):
        return message

    def on_handling_failed(self, message: Mapping[str, Any], error: Exception):
        raise error


DUMMY_HANDLER: _DummyHandler = _DummyHandler()
"""
Handler which just returns provided message attributes
(kind of an "identity function")
"""
