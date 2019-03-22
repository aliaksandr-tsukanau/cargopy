import logging
from typing import Mapping, Any, Optional, TypeVar, Generic

from attr import attrs

from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.pubsub import Publisher


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

    def on_received(self, message: Any):
        """
        Callback which is called as soon as pipeline is run.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param message: Message as it has been received, without any deserialization
        """
        _LOGGER.info(f"Received message:\n {message}")

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
            f"Message successfully deserialized into attributes:\n {parsed_message}"
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
            f"Was not able to deserialize the following message:\n{message}"
        )

    def on_handled(
        self,
        original_message: Any,
        parsed_message: Mapping[str, Any],
        result: HandlingResult,
    ):
        """
        Callback which is called right after message was handled (successfully or not).

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param result:
            Result fetched from handler (also shows if handling was successful)
        """
        _LOGGER.info(f"Message handled, status {result.status}")

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
        _LOGGER.info(f"Published result:\n{result}")

    def on_publishing_failed(
        self,
        original_message: Any,
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
        error: Exception,
    ):
        """
        Callback which is called write after message was published successfully.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param parsed_message: Message attributes after deserialization
        :param result:
            Result fetched from handler (also shows if handling was successful)
        :param error: exception object which was raised
        """
        _LOGGER.exception(f"Failed to publish result:\n{result}")

    def _when_parsing_succeeded(self, original: Any, parsed: Mapping[str, Any]):
        result = self.handler(parsed)
        self.on_handled(original_message=original, parsed_message=parsed, result=result)
        if self.publisher is not None:
            self._try_publish(original, parsed, result)

    def _when_parsing_failed(self, message: Any, error: Exception):
        if self.publisher is None:
            return
        assert self.deserializer is not None
        try:
            result = self.deserializer.build_error_result(message, error)
            handling_result = HandlingResult.err(result)
        except Exception:
            _LOGGER.exception(
                "Deserialization failed and error result cannot be built."
            )
        else:
            self._try_publish(original=message, parsed=None, result=handling_result)

    def _try_publish(
        self, original: Any, parsed: Optional[Mapping[str, Any]], result: HandlingResult
    ):
        assert self.publisher is not None
        try:
            self.publisher.publish_result(result)
            self.on_published(
                original_message=original, parsed_message=parsed, result=result
            )
        except Exception as e:
            self.on_publishing_failed(
                original_message=original, parsed_message=parsed, result=result, error=e
            )

    def _run_no_deser(self, message: Optional[Any]):
        if message is not None:
            if self.handler is DUMMY_HANDLER:
                self._when_parsing_succeeded(original=message, parsed=message)
            else:
                raise ValueError("No deserializer to parse non-empty message.")
        if message is None:
            self._when_parsing_succeeded(original=None, parsed={})

    def _after_on_received(self, message: Optional[Any]):
        try:
            assert self.deserializer is not None
            parsed = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_deserialization_failed(message, error=e)
            self._when_parsing_failed(message, error=e)
        else:
            self.on_deserialized(message, parsed)
            self._when_parsing_succeeded(original=message, parsed=parsed)

    def _run_with_deser(self, message: Optional[Any]):
        self.on_received(message)
        self._after_on_received(message)

    def run(self, message: Optional[Any] = None):
        """
        Method that starts execution of pipeline stages.
        :param message: Message as is, without deserialization.
            Or message attributes
            if the executor was instantiated with neither a deserializer nor a handler
            (useful to quickly publish message attributes by hand)
        """
        if self.deserializer is None:
            self._run_no_deser(message)
        else:
            self._run_with_deser(message)
