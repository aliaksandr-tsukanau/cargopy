from abc import ABC, abstractmethod
from typing import Callable, Any


class Subscriber(ABC):
    @abstractmethod
    def subscribe(self, callback: Callable[[Any], Any]):
        raise NotImplementedError

    @abstractmethod
    def ack(self, message):
        raise NotImplementedError
