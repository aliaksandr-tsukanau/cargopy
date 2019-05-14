import logging
import threading
import queue
from collections import namedtuple
from types import FunctionType
from typing import (
    Mapping,
    Any,
    Optional,
    TypeVar,
    Generic,
    Tuple,
    Union,
    Callable,
    Iterator,
)

from happyly.utils import generator_check
from happyly.exceptions import StopPipeline, FetchedNoResult
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.handling import Handler
from happyly.serialization.deserializer import Deserializer
from happyly.serialization.serializer import Serializer
from happyly.pubsub import BasePublisher
from happyly.serialization import DUMMY_SERDE
from happyly.pubsub import BaseSubscriber

_LOGGER = logging.getLogger(__name__)

D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=BasePublisher)
SE = TypeVar("SE", bound=Serializer)
S = TypeVar('S', bound=BaseSubscriber)


_Result = Optional[Mapping[str, Any]]
ResultAndDeserialized = namedtuple('ResultAndDeserialized', 'result deserialized')
HandlerClsOrFn = Union[Handler, Callable[[Mapping[str, Any]], _Result]]


def _deser_converter(deserializer: Union[Deserializer, Callable]):
    if isinstance(deserializer, FunctionType):
        return Deserializer.from_function(deserializer)
    elif isinstance(deserializer, Deserializer):
        return deserializer
    else:
        raise TypeError


def _publ_converter(publisher: Union[BasePublisher, Callable]):
    if isinstance(publisher, FunctionType):
        return BasePublisher.from_function(publisher)
    elif isinstance(publisher, BasePublisher):
        return publisher
    else:
        raise TypeError


def _ser_converter(serializer: Union[Serializer, Callable]):
    if isinstance(serializer, FunctionType):
        return Serializer.from_function(serializer)
    elif isinstance(serializer, Serializer):
        return serializer
    else:
        raise TypeError


class Executor(Generic[D, P, SE, S]):
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

    handler: HandlerClsOrFn
    """
    Provides implementation of handling stage to Executor.
    """

    deserializer: D
    # Why type:ignore? Because DUMMY_SERDE is a subclass of Deserializer
    # but not necessarily subclass of whatever D will be in runtime.
    """
    Provides implementation of deserialization stage to Executor.

    If not present, no deserialization is performed.
    """

    publisher: Optional[P]
    """
    Provides implementation of serialization and publishing stages to Executor.

    If not present, no publishing is performed.
    """

    serializer: SE

    subscriber: Optional[S]

    def __init__(
        self,
        handler: HandlerClsOrFn = DUMMY_HANDLER,
        deserializer: Optional[Union[D, Callable]] = None,
        publisher: Optional[Union[P, Callable]] = None,
        serializer: Optional[Union[SE, Callable]] = None,
        subscriber: Optional[S] = None,
    ):
        self.handler = handler  # type: ignore
        if deserializer is None:
            self.deserializer = DUMMY_SERDE  # type: ignore
        else:
            self.deserializer = _deser_converter(deserializer)

        if publisher is None:
            self.publisher = None
        else:
            self.publisher = _publ_converter(publisher)

        if serializer is None:
            self.serializer = DUMMY_SERDE  # type: ignore
        else:
            self.serializer = _ser_converter(serializer)

        self.subscriber = subscriber
        self.publisher_queue: queue.Queue = queue.Queue()

    def on_received(self, original_message: Any):
        """
        Callback which is called as soon as pipeline is run.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message: Message as it has been received,
            without any deserialization
        """
        _LOGGER.info(f"Received message: {original_message}")

    def on_deserialized(
        self, original_message: Any, deserialized_message: Mapping[str, Any]
    ):
        """
        Callback which is called right after message was deserialized successfully.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message: Message as it has been received,
            without any deserialization
        :param deserialized_message: Message attributes after deserialization
        """
        _LOGGER.info(
            'Message successfully deserialized into attributes: '
            f'{deserialized_message}'
        )

    def on_deserialization_failed(self, original_message: Any, error: Exception):
        """
        Callback which is called right after deserialization failure.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message: Message as it has been received,
            without any deserialization
        :param error: exception object which was raised
        """
        _LOGGER.exception('')
        _LOGGER.error(
            f"Was not able to deserialize the following message: {original_message}"
        )

    def on_handled(
        self,
        original_message: Any,
        deserialized_message: Mapping[str, Any],
        result: Optional[Mapping[str, Any]],
    ):
        """
        Callback which is called right after message was handled
        (successfully or not, but without raising an exception).

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param deserialized_message: Message attributes after deserialization
        :param result:
            Result fetched from handler
        """
        _LOGGER.info(f"Message handled, result: {result}.")

    def on_handling_failed(
        self,
        original_message: Any,
        deserialized_message: Mapping[str, Any],
        error: Exception,
    ):
        """
        Callback which is called if handler's `on_handling_failed`
        raises an exception.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param deserialized_message: Message attributes after deserialization
        :param error: exception object which was raised
        """
        _LOGGER.exception('')
        _LOGGER.error(f'Handler raised an exception.')

    def on_serialized(
        self,
        original_message: Any,
        deserialized_message: Optional[Mapping[str, Any]],
        result: _Result,
        serialized_message: Any,
    ):
        _LOGGER.debug('Serialized message.')

    def on_serialization_failed(
        self,
        original: Any,
        deserialized: Optional[Mapping[str, Any]],
        result: _Result,
        error: Exception,
    ):
        _LOGGER.exception('')
        _LOGGER.error('Was not able to deserialize message.')

    def on_published(
        self,
        original_message: Any,
        deserialized_message: Optional[Mapping[str, Any]],
        result: _Result,
        serialized_message: Any,
    ):
        """
        Callback which is called right after message was published successfully.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param deserialized_message: Message attributes after deserialization
        :param result:
            Result fetched from handler
        """
        _LOGGER.info(f"Published result: {result}")

    def on_publishing_failed(
        self,
        original_message: Any,
        deserialized_message: Optional[Mapping[str, Any]],
        result: _Result,
        serialized_message: Any,
        error: Exception,
    ):
        """
        Callback which is called when publisher fails to publish.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param original_message:
            Message as it has been received, without any deserialization
        :param deserialized_message: Message attributes after deserialization
        :param result:
            Result fetched from handler
        :param error: exception object which was raised
        """
        _LOGGER.exception('')
        _LOGGER.error(f"Failed to publish result: {result}")

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
        self
        # original: Any,
        # parsed: Optional[Mapping[str, Any]],
        # result: _Result,
        # serialized: Any,
    ):
        original, parsed, result, serialized = self.publisher_queue.get()
        assert self.publisher is not None
        try:
            self.publisher.publish(serialized)
        except Exception as e:
            self.on_publishing_failed(
                original_message=original,
                deserialized_message=parsed,
                result=result,
                serialized_message=serialized,
                error=e,
            )
            self.publisher_queue.task_done()
            raise e from e
        else:
            self.on_published(
                original_message=original,
                deserialized_message=parsed,
                result=result,
                serialized_message=serialized,
            )
            self.publisher_queue.task_done()

    def _fetch_deserialized_and_result(
        self, message: Optional[Any]
    ) -> Iterator[ResultAndDeserialized]:
        try:
            deserialized = self._deserialize(message)
        except StopPipeline as e:
            raise e from e
        except Exception as e:
            yield ResultAndDeserialized(
                result=self._build_error_result(message, e), deserialized=None
            )
            return

        for result in self._handle(message, deserialized):
            yield ResultAndDeserialized(result=result, deserialized=deserialized)

    def _deserialize(self, message: Optional[Any]):
        try:
            deserialized = self.deserializer.deserialize(message)
        except Exception as e:
            self.on_deserialization_failed(original_message=message, error=e)
            raise e from e
        else:
            self.on_deserialized(
                original_message=message, deserialized_message=deserialized
            )
            return deserialized

    def _build_error_result(self, message: Any, error: Exception):
        try:
            error_result = self.deserializer.build_error_result(message, error)
        except Exception as new_e:
            _LOGGER.exception('')
            _LOGGER.error("Deserialization failed and error result cannot be built.")
            raise new_e from new_e
        return error_result

    def _handle(self, message: Optional[Any], deserialized: Mapping[str, Any]):
        try:
            if generator_check.is_generator(self.handler):  # type: ignore
                for result in self.handler(deserialized):  # type: ignore
                    self.on_handled(  # type: ignore
                        original_message=message,
                        deserialized_message=deserialized,
                        result=result,
                    )
                    yield result
            else:
                result = self.handler(deserialized)  # type: ignore
                self.on_handled(
                    original_message=message,
                    deserialized_message=deserialized,
                    result=result,
                )
                yield result
                return
        except Exception as e:
            self.on_handling_failed(
                original_message=message, deserialized_message=deserialized, error=e
            )
            raise e from e

    def _serialize(
        self,
        original_message: Optional[Any],
        parsed_message: Optional[Mapping[str, Any]],
        result: Mapping[str, Any],
    ) -> Any:

        try:
            serialized = self.serializer.serialize(result)
        except Exception as e:
            self.on_serialization_failed(
                original=original_message,
                deserialized=parsed_message,
                result=result,
                error=e,
            )
        else:
            self.on_serialized(
                original_message=original_message,
                deserialized_message=parsed_message,
                result=result,
                serialized_message=serialized,
            )
            return serialized

    def _run_core(
        self, message: Optional[Any] = None
    ) -> Iterator[Tuple[Optional[Mapping[str, Any]], _Result, Optional[Any]]]:

        self.on_received(message)
        for result, deserialized in self._fetch_deserialized_and_result(message):
            if result is not None:
                serialized = self._serialize(message, deserialized, result)
            else:
                serialized = None
            yield deserialized, result, serialized

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
            publisher_thread = threading.Thread(target=self._try_publish, daemon=True)
            publisher_thread.start()

            for deserialized, result, serialized in self._run_core(message):
                if self.publisher is not None and serialized is not None:
                    assert (
                        result is not None
                    )  # something is serialized, so there must be a result
                    self.publisher_queue.put(
                        (message, deserialized, result, serialized)
                    )

            self.publisher_queue.join()
        except StopPipeline as e:
            self.on_stopped(original_message=message, reason=e.reason)
        except Exception as e:
            self.on_finished(original_message=message, error=e)
        else:
            self.on_finished(original_message=message, error=None)

    def run_for_result(self, message: Optional[Any] = None):
        try:
            if generator_check.is_generator(self.handler):  # type: ignore

                def func(m):
                    for _, _, res in self._run_core(m):
                        yield res

                result = func(message)
            else:
                _, _, result = next(self._run_core(message))
        except StopPipeline as e:
            self.on_stopped(original_message=message, reason=e.reason)
            raise FetchedNoResult from e
        except Exception as e:
            self.on_finished(original_message=message, error=e)
            raise FetchedNoResult from e
        else:
            self.on_finished(original_message=message, error=None)
            return result

    def start_listening(self):
        if self.subscriber is None:
            raise Exception('Cannot subscribe since subscriber is not initialized.')
        return self.subscriber.subscribe(callback=self.run)


if __name__ == '__main__':

    def a(m):
        for i in range(3):
            yield {"a": str(i)}

    class StoppingExecutor(Executor):
        def on_deserialized(
            self, original_message: Any, deserialized_message: Mapping[str, Any]
        ):
            super().on_deserialized(original_message, deserialized_message)
            raise StopPipeline("the sky is very high")

    logging.basicConfig(level=logging.DEBUG)

    StoppingExecutor(lambda m: {'2': 42}).run()  # type: ignore
    import time

    time.sleep(1)
    res = Executor(a).run_for_result()
    for r in res:
        print(r)
