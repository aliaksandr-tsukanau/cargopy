import logging
from typing import Mapping, Any, Optional, TypeVar, Generic

from attr import attrs

from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.pubsub import Publisher


_LOGGER = logging.getLogger(__name__)

D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)


@attrs(auto_attribs=True)
class Executor(Generic[D, P]):
    handler: Handler
    deserializer: Optional[D] = None
    publisher: Optional[P] = None

    def on_received(self, message: Any):
        pass

    def on_deserialized(self, original_message: Any, parsed_message: Mapping[str, Any]):
        pass

    def on_deserialization_failed(self, message: Any, error: Exception):
        pass

    def on_handled(
        self,
        original_message: Any,
        parsed_message: Mapping[str, Any],
        result: HandlingResult,
    ):
        pass

    def on_published(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
    ):
        pass

    def on_publishing_failed(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
        error: Exception,
    ):
        pass

    def _when_parsing_succeeded(self, original: Any, parsed: Mapping[str, Any]):
        result = self.handler(parsed)
        _LOGGER.info(f"Message handled, status {result.status}")
        self.on_handled(original_message=original, parsed_message=parsed, result=result)
        if self.publisher is not None:
            self._try_publish(original, parsed, result)

    def _when_parsing_failed(self, message: Any, error: Exception):
        if self.publisher is None:
            return
        assert self.deserializer is not None
        result = self.deserializer.build_error_result(message, error)
        handling_result = HandlingResult.err(result)
        self._try_publish(original=message, parsed=None, result=handling_result)

    def _try_publish(
        self, original: Any, parsed: Optional[Mapping[str, Any]], result: HandlingResult
    ):
        assert self.publisher is not None
        try:
            self.publisher.publish_result(result)
            _LOGGER.info(f"Published result:\n{result}")
            self.on_published(
                original_message=original, parsed_message=parsed, result=result
            )
        except Exception as e:
            _LOGGER.exception("Failed to publish result:\n{result}")
            self.on_publishing_failed(
                original_message=original, parsed_message=parsed, result=result, error=e
            )

    def _run_no_deser(self, message: Optional[Any]):
        if message is not None:
            raise ValueError("No deserializer to parse non-empty message.")
        if message is None:
            self._when_parsing_succeeded(original=None, parsed={})

    def _after_on_received(self, message: Optional[Any]):
        try:
            assert self.deserializer is not None
            parsed = self.deserializer.deserialize(message)
        except Exception as e:
            _LOGGER.exception(
                f"Was not able to deserialize the following message\n{message}"
            )
            self.on_deserialization_failed(message, error=e)
            self._when_parsing_failed(message, error=e)
        else:
            _LOGGER.debug(
                f"Message successfully deserialized into attributes:\n {parsed}"
            )
            self.on_deserialized(message, parsed)
            self._when_parsing_succeeded(original=message, parsed=parsed)

    def _run_with_deser(self, message: Optional[Any]):
        _LOGGER.info(f"Received message:\n {message}")
        self.on_received(message)
        self._after_on_received(message)

    def run(self, message: Optional[Any] = None):
        if self.deserializer is None:
            self._run_no_deser(message)
        else:
            self._run_with_deser(message)
