import logging
from typing import Any

from attr import attrs, attrib

from happyly.pubsub.subscriber import Subscriber
from .executor import Executor


@attrs(auto_attribs=True, frozen=True)
class Listener(Executor):
    subscriber: Subscriber = attrib(kw_only=True)

    def on_acknowledged(self, message: Any):
        pass

    def on_received(self, message: Any):
        super().on_received(message)
        self.subscriber.ack(message)
        self.on_acknowledged(message)

    def start_listening(self):
        return self.subscriber.subscribe(callback=self.run)
