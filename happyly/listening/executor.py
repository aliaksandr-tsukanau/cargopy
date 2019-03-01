from typing import Mapping, Any, Optional

from attr import attrs

from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.pubsub import Publisher


@attrs(auto_attribs=True, frozen=True)
class Executor:
    handler: Handler
    deserializer: Optional[Deserializer] = None
    publisher: Optional[Publisher] = None

    def on_received(self, message: Any):
        pass

    def on_acknowledged(self, message: Any):
        pass

    def on_parsed(self, original_message: Any, parsed_message: Mapping[str, Any]):
        pass

    def on_parsing_failed(self, message: Any, error: Exception):
        pass

    def on_handled(self, result: HandlingResult):
        pass

    def on_published(self, result: HandlingResult):
        pass

    def on_publishing_failed(self, result: HandlingResult, error: Exception):
        pass

    def _when_parsing_succeeded(self, parsed: Mapping[str, Any]):
        result = self.handler(parsed)
        self.on_handled(result)
        if self.publisher is not None:
            self._try_publish(result)

    def _when_parsing_failed(self, message: Any, error: Exception):
        if self.publisher is None:
            return
        result = self.deserializer.build_error_result(message, error)
        handling_result = HandlingResult.err(result)
        self._try_publish(handling_result)

    def _try_publish(self, result: HandlingResult):
        try:
            self.publisher.publish_result(result)
            self.on_published(result)
        except Exception as e:
            self.on_publishing_failed(result, error=e)

    def run(self, message: Optional[Any] = None):
        if message is None:
            self._when_parsing_succeeded({})
            return
        self.on_received(message)
        try:
            parsed = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_parsing_failed(message, error=e)
            self._when_parsing_failed(message, error=e)
        else:
            self.on_parsed(message, parsed)
            self._when_parsing_succeeded(parsed=parsed)
