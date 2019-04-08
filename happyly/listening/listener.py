"""
:class:`~happyly.listening.listener.BaseListener` and its subclasses.
Listener is a form of Executor
which is able to run pipeline by an event coming from a subscription.
"""

import logging
from typing import Any, TypeVar, Optional, Generic

from happyly.serialization.serializer import Serializer
from happyly.serialization.dummy import DUMMY_SERDE
from happyly.handling import Handler
from happyly.pubsub import BasePublisher
from happyly.pubsub.subscriber import BaseSubscriber, SubscriberWithAck
from happyly.serialization import Deserializer
from .executor import Executor


_LOGGER = logging.getLogger(__name__)


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=BasePublisher)
S = TypeVar("S", bound=BaseSubscriber)
SE = TypeVar("SE", bound=Serializer)


class BaseListener(Executor[D, P, SE], Generic[D, P, SE, S]):
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

    subscriber: S
    """
    Provides implementation of how to subscribe.
    """

    def __init__(  # type: ignore
        self,
        subscriber: S,
        handler: Handler,
        deserializer: D,
        serializer: SE = DUMMY_SERDE,  # type: ignore
        publisher: Optional[P] = None,
    ):
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            publisher=publisher,
            serializer=serializer,
        )
        self.subscriber = subscriber

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)


class ListenerWithAck(BaseListener[D, P, SE, SubscriberWithAck], Generic[D, P, SE]):
    """
    Acknowledge-aware listener.
    Defines :meth:`ListenerWithAck.ack` method.
    Subclass :class:`ListenerWithAck` and specify when to ack
    by overriding the corresponding callbacks.
    """

    def __init__(  # type: ignore
        self,
        subscriber: SubscriberWithAck,
        handler: Handler,
        deserializer: D,
        serializer: SE = DUMMY_SERDE,
        publisher: Optional[P] = None,
    ):
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            serializer=serializer,
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


class EarlyAckListener(ListenerWithAck[D, P, SE], Generic[D, P, SE]):
    """
    Acknowledge-aware :class:`BaseListener`,
    which performs :meth:`.ack` right after
    :meth:`.on_received` callback is finished.
    """

    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)


class LateAckListener(ListenerWithAck[D, P, SE], Generic[D, P, SE]):
    """
    Acknowledge-aware listener,
    which performs :meth:`.ack` at the very end of pipeline.
    """

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)
