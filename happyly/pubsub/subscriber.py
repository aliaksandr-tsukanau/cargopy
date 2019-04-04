from abc import ABC, abstractmethod
from typing import Callable, Any


class BaseSubscriber(ABC):
    @abstractmethod
    def subscribe(self, callback: Callable[[Any], Any]):
        raise NotImplementedError


class SubscriberWithAck(BaseSubscriber, ABC):
    @abstractmethod
    def ack(self, message):
        raise NotImplementedError
