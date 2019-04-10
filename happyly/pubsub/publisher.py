from abc import ABC, abstractmethod
from typing import Any, Callable


class BasePublisher(ABC):
    @abstractmethod
    def publish(self, serialized_message: Any):
        raise NotImplementedError("No default implementation in base publisher class")

    @classmethod
    def from_function(cls, func: Callable[[Any], None]):
        def publish(self, serialized_message: Any):
            func(serialized_message)

        constructed_type = type(
            '__GeneratedPublisher', (BasePublisher,), {'publish': publish}
        )
        return constructed_type()
