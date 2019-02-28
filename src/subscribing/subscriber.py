from abc import ABC, abstractmethod
from typing import Callable, Any

from google.cloud import pubsub_v1

from listening.message import Message


class Subscriber(ABC):

    @abstractmethod
    def subscribe(self, callback: Callable[[Message], Any]):
        raise NotImplementedError('No default implementation in base Subscriber class')


Subscriber.register(pubsub_v1.SubscriberClient)
