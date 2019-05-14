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


BaseListener = Executor


class ExecutorWithAck(Executor[D, P, SE, SubscriberWithAck], Generic[D, P, SE]):
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
        if self.subscriber is None:
            raise Exception('Cannot ack since subscriber is not initialized.')
        self.subscriber.ack(message)
        self.on_acknowledged(message)


class EarlyAckExecutor(ExecutorWithAck[D, P, SE], Generic[D, P, SE]):
    """
    Acknowledge-aware :class:`BaseListener`,
    which performs :meth:`.ack` right after
    :meth:`.on_received` callback is finished.
    """

    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)


class LateAckExecutor(ExecutorWithAck[D, P, SE], Generic[D, P, SE]):
    """
    Acknowledge-aware listener,
    which performs :meth:`.ack` at the very end of pipeline.
    """

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)


ListenerWithAck = ExecutorWithAck
EarlyAckListener = EarlyAckExecutor
LateAckListener = LateAckExecutor
