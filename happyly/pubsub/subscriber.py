from abc import ABC, abstractmethod
from typing import Callable, Any

from happyly._deprecations.utils import will_be_removed


class BaseSubscriber(ABC):
    @abstractmethod
    def subscribe(self, callback: Callable[[Any], Any]):
        raise NotImplementedError


class SubscriberWithAck(BaseSubscriber, ABC):
    @abstractmethod
    def ack(self, message):
        raise NotImplementedError


# for compatibility, to be deprecated
class Subscriber(SubscriberWithAck, ABC):
    def __init__(self, *args, **kwargs):
        will_be_removed(SubscriberWithAck, '0.7.0')
        super().__init__(*args, **kwargs)
