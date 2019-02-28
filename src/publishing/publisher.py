from abc import ABC, abstractmethod
from typing import Optional

from handling import HandlingResult


class Publisher(ABC):

    def __init__(self,
                 publish_all_to: Optional[str] = None,
                 publish_success_to: Optional[str] = None,
                 publish_failure_to: Optional[str] = None,
                 ):
        if publish_all_to is not None and all(p is None for p in [publish_success_to, publish_failure_to]):
            self.publish_success_to = publish_all_to
            self.publish_failure_to = publish_all_to
        elif publish_all_to is None and all(p is not None for p in [publish_success_to, publish_failure_to]):
            self.publish_success_to = publish_success_to
            self.publish_failure_to = publish_failure_to
        else:
            raise ValueError(
                'Provide "publish_all_to" only, or else provide both "publish_success_to" and "publish_failure_to"'
            )

    @abstractmethod
    def publish(self, result: HandlingResult):
        raise NotImplementedError('No default implementation in base Publisher class')
