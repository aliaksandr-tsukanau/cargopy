from typing import Any, TypeVar

from attr import attrs, attrib

from happyly.pubsub import Publisher
from happyly.pubsub.subscriber import Subscriber
from happyly.serialization import Deserializer
from .executor import Executor


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)


@attrs(auto_attribs=True, frozen=True)
class Listener(Executor[D, P]):
    subscriber: Subscriber = attrib(kw_only=True)

    def on_acknowledged(self, message: Any):
        pass

    def on_received(self, message: Any):
        super().on_received(message)
        self.subscriber.ack(message)
        self.on_acknowledged(message)

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)
