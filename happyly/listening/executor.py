import logging
from typing import Mapping, Any, Optional, TypeVar, Generic

from attr import attrs

from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.pubsub import Publisher


_LOGGER = logging.getLogger(__name__)

D = TypeVar('D', bound=Deserializer)
P = TypeVar('P', bound=Publisher)


@attrs(auto_attribs=True, frozen=True)
class Executor(Generic[D, P]):
    handler: Handler
    deserializer: Optional[D] = None
    publisher: Optional[P] = None

    def on_received(self, message: Any):
        _LOGGER.info(f'Received message:\n {message}')

    def on_deserialized(self, original_message: Any, parsed_message: Mapping[str, Any]):
        _LOGGER.debug(f'Message successfully deserialized into attributes:\n {parsed_message}')

    def on_deserialization_failed(self, message: Any, error: Exception):
        _LOGGER.exception(f"Was not able to deserialize the following message\n{message}")

    def on_handled(self, original_message: Any, parsed_message: Mapping[str, Any], result: HandlingResult):
        _LOGGER.info(f'Message handled, status {result.status}')

    def on_published(self, original_message: Any, parsed_message: Optional[Mapping[str, Any]], result: HandlingResult):
        _LOGGER.info(f'Published result:\n{result}')

    def on_publishing_failed(self,
                             original_message: Any,
                             parsed_message: Optional[Mapping[str, Any]],
                             result: HandlingResult,
                             error: Exception,
                             ):
        _LOGGER.exception('Failed to publish result:\n{result}')

    def _when_parsing_succeeded(self, original: Any, parsed: Mapping[str, Any]):
        result = self.handler(parsed)
        self.on_handled(
            original_message=original,
            parsed_message=parsed,
            result=result,
        )
        if self.publisher is not None:
            self._try_publish(result)

    def _when_parsing_failed(self, message: Any, error: Exception):
        if self.publisher is None:
            return
        result = self.deserializer.build_error_result(message, error)
        handling_result = HandlingResult.err(result)
        self._try_publish(
            original=message,
            parsed=None,
            result=handling_result,
        )

    def _try_publish(self, original: Any, parsed: Optional[Mapping[str, Any]], result: HandlingResult):
        try:
            self.publisher.publish_result(result)
            self.on_published(
                original_message=original,
                parsed_message=parsed,
                result=result,
            )
        except Exception as e:
            self.on_publishing_failed(
                original_message=original,
                parsed_message=parsed,
                result=result,
                error=e,
            )

    def run(self, message: Optional[Any] = None):
        if message is None:
            self._when_parsing_succeeded(original=None, parsed={})
            return
        self.on_received(message)
        try:
            parsed = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_deserialization_failed(message, error=e)
            self._when_parsing_failed(message, error=e)
        else:
            self.on_deserialized(message, parsed)
            self._when_parsing_succeeded(
                original=message,
                parsed=parsed,
            )
