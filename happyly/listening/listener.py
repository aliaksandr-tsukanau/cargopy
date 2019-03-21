import warnings
from typing import Any, TypeVar, Optional, Generic

from happyly.handling import Handler
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.pubsub import Publisher
from happyly.pubsub.subscriber import BaseSubscriber, SubscriberWithAck
from happyly.serialization import Deserializer
from .executor import Executor


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)
S = TypeVar("S", bound=BaseSubscriber)


class BaseListener(Executor[D, P], Generic[D, P, S]):
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

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)


class EarlyAckListener(BaseListener[D, P, SubscriberWithAck], Generic[D, P]):
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
        pass

    def _after_on_received(self, message: Optional[Any]):
        self.subscriber.ack(message)
        self.on_acknowledged(message)
        super()._after_on_received(message)


class LateAckListener(BaseListener[D, P, SubscriberWithAck], Generic[D, P]):
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
        pass

    def _after_on_received(self, message: Optional[Any]):
        super()._after_on_received(message)
        self.subscriber.ack(message)
        self.on_acknowledged(message)


# for compatibility, to be deprecated
class Listener(EarlyAckListener[D, P]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            """Please use EarlyAckListener instead,
            Listener will be deprecated in the future""",
            PendingDeprecationWarning,
        )
