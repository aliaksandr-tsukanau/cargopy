from typing import Any, TypeVar, Optional

from happyly.handling import Handler
from happyly.handling.dummy_handler import DUMMY_HANDLER
from happyly.pubsub import Publisher
from happyly.pubsub.subscriber import Subscriber
from happyly.serialization import Deserializer
from .executor import Executor


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)


class Listener(Executor[D, P]):
    def __init__(
        self,
        subscriber: Subscriber,
        handler: Handler,
        deserializer: Optional[D] = None,
        publisher: Optional[P] = None,
    ):
        assert handler is not DUMMY_HANDLER
        super().__init__(
            handler=handler, deserializer=deserializer, publisher=publisher
        )
        self.subscriber: Subscriber = subscriber

    def __attrs_post_init__(self):
        assert self.handler is not DUMMY_HANDLER

    def on_acknowledged(self, message: Any):
        pass

    def _after_on_received(self, message: Optional[Any]):
        self.subscriber.ack(message)
        self.on_acknowledged(message)
        super()._after_on_received(message)

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)
