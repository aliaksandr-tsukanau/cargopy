import logging
from collections import namedtuple
from typing import Mapping, Any, Optional, TypeVar, Generic, Tuple

from attr import attrs

from happyly import serialization
from happyly.exceptions import StopPipeline, FetchedNoResult
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.handling import Handler, HandlingResult
from happyly.serialization.deserializer import Deserializer
from happyly.serialization.serializer import Serializer
from happyly.pubsub import Publisher
from happyly.serialization import DUMMY_SERDE

_LOGGER = logging.getLogger(__name__)

D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)
SE = TypeVar("SE", bound=Serializer)


ResultAndDeserialized = namedtuple('ResultAndDeserialized', 'result deserialized')


@attrs(auto_attribs=True)
class Executor(Generic[D, P, SE]):
    """
    Component which is able to run handler as a part of more complex pipeline.

    Implements managing of stages inside the pipeline
    (deserialization, handling, serialization, publishing)
    and introduces callbacks between the stages which can be easily overridden.

    Executor does not implement stages themselves,
    it takes internal implementation of stages from corresponding components:
    :class:`Handler`, :class:`Deserializer`, :class:`Publisher`.

    It means that :class:`Executor` is universal
    and can work with any serialization/messaging technology
    depending on concrete components provided to executor's constructor.
    """

    handler: Handler = DUMMY_HANDLER
    """
    Provides implementation of handling stage to Executor.
    """

    deserializer: D = DUMMY_SERDE  # type: ignore
    """
    Provides implementation of deserialization stage to Executor.

    If not present, no deserialization is performed.
    """

    publisher: Optional[P] = None
    """
    Provides implementation of serialization and publishing stages to Executor.

    If not present, no publishing is performed.
    """

    serializer: SE = DUMMY_SERDE  # type: ignore

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

    def on_serialized(
        self,
        original: Any,
        deserialized: Optional[Mapping[str, Any]],
        result: HandlingResult,
        serialized: Any,
    ):
        _LOGGER.debug('Serialized message.')

    def on_serialization_failed(
        self,
        original: Any,
        deserialized: Optional[Mapping[str, Any]],
        result: HandlingResult,
        error: Exception,
    ):
        _LOGGER.exception('Was not able to deserialize message.')

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
        Is guaranteed to be called unless pipeline is stopped via
        StopPipeline.

        :param original_message:
            Message as it has been received, without any deserialization
        :param error: exception object which was raised or None
        """
        _LOGGER.info('Pipeline execution finished.')

    def on_stopped(self, original_message: Any, reason: str = ''):
        """
        Callback which is called when pipeline is stopped via
        :exc:`.StopPipeline`

        :param original_message:
            Message as it has been received, without any deserialization
        :param reason: message describing why the pipeline stopped
        """
        s = "." if reason == "" else f" due to the reason: {reason}."
        _LOGGER.info(f'Stopped pipeline{s}')

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
            raise e from e
        else:
            self.on_published(
                original_message=original, parsed_message=parsed, result=result
            )

    def _fetch_deserialized_and_result(
        self, message: Optional[Any]
    ) -> ResultAndDeserialized:
        try:
            deserialized = self._deserialize(message)
        except StopPipeline as e:
            raise e from e
        except Exception as e:
            retval = ResultAndDeserialized(
                result=self._build_error_result(message, e), deserialized=None
            )
            return retval
        retval = ResultAndDeserialized(
            result=self._handle(message, deserialized), deserialized=deserialized
        )
        return retval

    def _deserialize(self, message: Optional[Any]):
        try:
            deserialized = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_deserialization_failed(message=message, error=e)
            raise e from e
        else:
            self.on_deserialized(original_message=message, parsed_message=deserialized)
            return deserialized

    def _build_error_result(self, message: Any, error: Exception):
        try:
            error_result = self.deserializer.build_error_result(message, error)
        except Exception as new_e:
            _LOGGER.exception(
                "Deserialization failed and error result cannot be built."
            )
            raise new_e from new_e
        return HandlingResult.err(error_result)

    def _handle(self, message: Optional[Any], deserialized: Mapping[str, Any]):
        try:
            result = self.handler(deserialized)
        except Exception as e:
            self.on_handling_failed(
                original_message=message, parsed_message=deserialized, error=e
            )
            raise e from e
        self.on_handled(
            original_message=message, parsed_message=deserialized, result=result
        )
        return result

    def _serialize(
        self,
        original_message: Optional[Any],
        parsed_message: Optional[Mapping[str, Any]],
        result: HandlingResult,
    ) -> Any:

        try:
            serialized = serialization.utils.serialize_with_dispatching(
                self.serializer, result.data
            )
        except Exception as e:
            self.on_serialization_failed(
                original=original_message,
                deserialized=parsed_message,
                result=result,
                error=e,
            )
        else:
            self.on_serialized(
                original=original_message,
                deserialized=parsed_message,
                result=result,
                serialized=serialized,
            )
            return serialized

    def _run_core(
        self, message: Optional[Any] = None
    ) -> Tuple[Optional[Mapping[str, Any]], Optional[HandlingResult], Optional[Any]]:

        self.on_received(message)
        result, deserialized = self._fetch_deserialized_and_result(message)
        if result is not None:
            serialized = self._serialize(message, deserialized, result)
        else:
            serialized = None
        return deserialized, result, serialized

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
            deserialized, result, serialized = self._run_core(message)
            if self.publisher is not None and serialized is not None:
                assert (
                    result is not None
                )  # something is serialized, so there must be a result
                self.on_finished(original_message=message, error=None)
                self._try_publish(message, deserialized, result)
        except StopPipeline as e:
            self.on_stopped(original_message=message, reason=e.reason)
        except Exception as e:
            self.on_finished(original_message=message, error=e)
        else:
            self.on_finished(original_message=message, error=None)

    def run_for_result(self, message: Optional[Any] = None):
        try:
            _, _, serialized = self._run_core(message)
        except StopPipeline as e:
            self.on_stopped(original_message=message, reason=e.reason)
            raise FetchedNoResult from e
        except Exception as e:
            self.on_finished(original_message=message, error=e)
            raise FetchedNoResult from e
        else:
            self.on_finished(original_message=message, error=None)
            return serialized


if __name__ == '__main__':

    class StoppingExecutor(Executor):
        def on_deserialized(
            self, original_message: Any, parsed_message: Mapping[str, Any]
        ):
            super().on_deserialized(original_message, parsed_message)
            raise StopPipeline("the sky is very high")

    logging.basicConfig(level=logging.DEBUG)

    StoppingExecutor(lambda m: HandlingResult.ok(42)).run()  # type: ignore
    print(
        Executor(  # type: ignore
            lambda m: HandlingResult.ok({"spam": "eggs"})
        ).run_for_result()
    )
