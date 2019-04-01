import logging
from typing import Mapping, Any, Optional, TypeVar, Generic

from attr import attrs

from happyly.exceptions import StopPipeline
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.pubsub import Publisher
from happyly.serialization import DUMMY_DESERIALIZER

_LOGGER = logging.getLogger(__name__)

D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)


@attrs(auto_attribs=True)
class Executor(Generic[D, P]):
    """
    Component which is able to run handler as a part of more complex pipeline.

    Implements managing of stages inside the pipeline
    (deserialization, handling, serialization, publishing)
    and introduces callbacks between the stages which can be easily overridden.

    Executor does not implement stages themselves,
    it takes internal implementation of stages from corresponding components:
    handler, deserializer, publisher.

    It means that executor is universal
    and can work with any serialization/messaging technology
    depending on concrete components provided to executor's constructor.
    """

    handler: Handler = DUMMY_HANDLER
    """
    Provides implementation of handling stage to Executor.
    """

    deserializer: Optional[D] = None
    """
    Provides implementation of deserialization stage to Executor.

    If not present, no deserialization is performed.
    """

    publisher: Optional[P] = None
    """
    Provides implementation of serialization and publishing stages to Executor.

    If not present, no publishing is performed.
    """

    def __attrs_post_init__(self):
        if self.deserializer is None:
            self.deserializer = DUMMY_DESERIALIZER

    def on_received(self, message: Any):
        """
        Callback which is called as soon as pipeline is run.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param message: Message as it has been received, without any deserialization
        """
        _LOGGER.info(f"Received message: {message}")

    def on_deserialized(self, original_message: Any, parsed_message: Mapping[str, Any]):
        """
        Callback which is called right after message was deserialized successfully.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message: Message as it has been received,
            without any deserialization
        :param parsed_message: Message attributes after deserialization
        """
        _LOGGER.info(
            f"Message successfully deserialized into attributes: {parsed_message}"
        )

    def on_deserialization_failed(self, message: Any, error: Exception):
        """
        Callback which is called right after deserialization failure.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param message: Message as it has been received, without any deserialization
        :param error: exception object which was raised
        """
        _LOGGER.exception(
            f"Was not able to deserialize the following message: {message}"
        )

    def on_handled(
        self,
        original_message: Any,
        parsed_message: Mapping[str, Any],
        result: HandlingResult,
    ):
        """
        Callback which is called right after message was handled
        (successfully or not, but without raising an exception).

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param result:
            Result fetched from handler (also shows if handling was successful)
        """
        _LOGGER.info(f"Message handled, status {result.status}")

    def on_handling_failed(
        self, original_message: Any, parsed_message: Mapping[str, Any], error: Exception
    ):
        """
        Callback which is called if handler's `on_handling_failed`
        raises an exception.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param error: exception object which was raised
        """
        _LOGGER.exception(f'Handler raised an exception.')

    def on_published(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
    ):
        """
        Callback which is called right after message was published successfully.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param result:
            Result fetched from handler (also shows if handling was successful)
        """
        _LOGGER.info(f"Published result: {result}")

    def on_publishing_failed(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
        error: Exception,
    ):
        """
        Callback which is called when publisher fails to publish.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param result:
            Result fetched from handler (also shows if handling was successful)
        :param error: exception object which was raised
        """
        _LOGGER.exception(f"Failed to publish result: {result}")

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        """
        Callback which is called when pipeline finishes its execution.
        Is guaranteed to be called, whether pipeline succeeds or not.

        :param original_message:
            Message as it has been received, without any deserialization
        :param error: exception object which was raised or None
        """
        _LOGGER.info('Pipeline execution finished.')

    def _when_parsing_succeeded(self, original: Any, parsed: Mapping[str, Any]):
        try:
            result = self.handler(parsed)
        except Exception as e:
            self.on_handling_failed(original, parsed, e)
            self.on_finished(original, e)
            return
        else:
            self.on_handled(
                original_message=original, parsed_message=parsed, result=result
            )
        if self.publisher is not None:
            self._try_publish(original, parsed, result)
        else:
            self.on_finished(original_message=original, error=None)

    def _when_parsing_failed(self, message: Any, error: Exception):
        assert self.deserializer is not None

        if self.publisher is None:
            self.on_finished(original_message=message, error=error)
            return
        try:
            result = self.deserializer.build_error_result(message, error)
            handling_result = HandlingResult.err(result)
        except Exception as new_err:
            _LOGGER.exception(
                "Deserialization failed and error result cannot be built."
            )
            self.on_finished(message, new_err)
        else:
            self._try_publish(original=message, parsed=None, result=handling_result)

    def _try_publish(
        self, original: Any, parsed: Optional[Mapping[str, Any]], result: HandlingResult
    ):
        assert self.publisher is not None
        try:
            self.publisher.publish_result(result)
        except Exception as e:
            self.on_publishing_failed(
                original_message=original, parsed_message=parsed, result=result, error=e
            )
            self.on_finished(original, error=e)
        else:
            self.on_published(
                original_message=original, parsed_message=parsed, result=result
            )
            self.on_finished(original, error=None)

    def _after_on_received(self, message: Optional[Any]):
        assert self.deserializer is not None
        try:
            parsed = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_deserialization_failed(message, error=e)
            self._when_parsing_failed(message, error=e)
        else:
            self.on_deserialized(message, parsed)
            self._when_parsing_succeeded(original=message, parsed=parsed)

    def run(self, message: Optional[Any] = None):
        """
        Method that starts execution of pipeline stages.

        To stop the pipeline
        raise StopPipeline inside any callback.

        :param message: Message as is, without deserialization.
            Or message attributes
            if the executor was instantiated with neither a deserializer nor a handler
            (useful to quickly publish message attributes by hand)
        """
        try:
            self.on_received(message)
            self._after_on_received(message)
        except StopPipeline as e:
            s = "." if e.reason == "" else f" due to the reason: {e.reason}."
            _LOGGER.info(f'Stopped pipeline{s}')


if __name__ == '__main__':

    class StoppingExecutor(Executor):
        def on_deserialized(
            self, original_message: Any, parsed_message: Mapping[str, Any]
        ):
            super().on_deserialized(original_message, parsed_message)
            raise StopPipeline("the sky is very high")

    logging.basicConfig(level=logging.INFO)

    StoppingExecutor(lambda m: HandlingResult.ok(42)).run()  # type: ignore
    Executor(lambda m: HandlingResult.ok(42)).run()  # type: ignore
