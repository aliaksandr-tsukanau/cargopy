from abc import ABC, abstractmethod
from typing import Callable, Any

from listening import Message


class Subscriber(ABC):

    @abstractmethod
    def subscribe(self, callback: Callable[[Message], Any]):
        pass
