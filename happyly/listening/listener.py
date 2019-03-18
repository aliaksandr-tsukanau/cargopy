from typing import Any, TypeVar, Optional

from attr import attrs, attrib

from happyly.pubsub import Publisher
from happyly.pubsub.subscriber import Subscriber
from happyly.serialization import Deserializer
from .executor import Executor


D = TypeVar("D", bound=Deserializer)
P = TypeVar("P", bound=Publisher)


@attrs(auto_attribs=True)
class Listener(Executor[D, P]):
    subscriber: Subscriber = attrib(kw_only=True)

    def on_acknowledged(self, message: Any):
        pass

    def _after_on_received(self, message: Optional[Any]):
        self.subscriber.ack(message)
        self.on_acknowledged(message)
        super()._after_on_received(message)

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)
