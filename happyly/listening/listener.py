import logging
from typing import Any, TypeVar, Optional, Generic

from happyly._deprecations.utils import will_be_removed
from happyly.handling import Handler
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.pubsub import Publisher
from happyly.pubsub.subscriber import BaseSubscriber, SubscriberWithAck
from happyly.serialization import Deserializer
from .executor import Executor


_LOGGER = logging.getLogger(__name__)


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)
S = TypeVar("S", bound=BaseSubscriber)


class BaseListener(Executor[D, P], Generic[D, P, S]):
    """
    Listener is a form of Executor
    which is able to run pipeline by an event coming from a subscription.

    Listener itself doesn't know how to subscribe,
    it subscribes via a provided subscriber.

    As any executor, implements managing of stages inside the pipeline
    (deserialization, handling, serialization, publishing)
    and contains callbacks between the stages which can be easily overridden.

    As any executor, listener does not implement stages themselves,
    it takes internal implementation of stages from corresponding components:
    handler, deserializer, publisher.

    It means that listener is universal
    and can work with any serialization/messaging technology
    depending on concrete components provided to listener's constructor.
    """

    def __init__(
        self,
        subscriber: S,
        handler: Handler,
        deserializer: Optional[D] = None,
        publisher: Optional[P] = None,
    ):
        assert handler is not DUMMY_HANDLER

        super().__init__(
            handler=handler, deserializer=deserializer, publisher=publisher
        )
        self.subscriber: S = subscriber
        """
        Provides implementation of how to subscribe.
        """

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)


class ListenerWithAck(BaseListener[D, P, SubscriberWithAck], Generic[D, P]):
    """
    Acknowledge-aware listener.
    Defines `ListenerWithAck.ack()`.
    Subclass ListenerWithAck and specify when to ack
    by overriding the corresponding callbacks.
    """

    def __init__(
        self,
        subscriber: SubscriberWithAck,
        handler: Handler,
        deserializer: Optional[D] = None,
        publisher: Optional[P] = None,
    ):
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            publisher=publisher,
            subscriber=subscriber,
        )

    def on_acknowledged(self, message: Any):
        """
        Callback which is called write after message was acknowledged.

        Override it in your custom Executor/Listener if needed,
        but don't forget to call implementation from base class.

        :param message:
            Message as it has been received, without any deserialization
        """
        _LOGGER.info('Message acknowledged')

    def ack(self, message: Any):
        """
        Acknowledge the message using implementation from subscriber,
        then log success.
        :param message:
            Message as it has been received, without any deserialization
        """
        self.subscriber.ack(message)
        self.on_acknowledged(message)


class EarlyAckListener(ListenerWithAck[D, P], Generic[D, P]):
    """
    Acknowledge-aware listener,
    which performs `ack` right after
    `on_received` callback is finished.
    """

    def _after_on_received(self, message: Optional[Any]):
        self.ack(message)
        super()._after_on_received(message)


class LateAckListener(ListenerWithAck[D, P], Generic[D, P]):
    """
    Acknowledge-aware listener,
    which performs `ack` at the very end of pipeline.
    """

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)


class Listener(EarlyAckListener[D, P], Generic[D, P]):
    def __init__(self, *args, **kwargs):
        will_be_removed(EarlyAckListener, '0.7.0')
        super().__init__(*args, **kwargs)
