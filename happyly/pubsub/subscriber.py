import warnings
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


# for compatibility, to be deprecated
class Subscriber(SubscriberWithAck, ABC):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Please use SubscriberWithAck instead, "
            "Subscriber will be deprecated in the future.",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
