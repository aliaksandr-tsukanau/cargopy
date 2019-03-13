from abc import ABC, abstractmethod
from typing import Optional, Mapping, Any, List

from happyly.handling import HandlingResult, HandlingResultStatus
from happyly.serialization.serializer import Serializer


class Publisher(ABC):
    def __init__(
        self,
        serializer: Serializer,
        publish_all_to: Optional[str] = None,
        publish_success_to: Optional[str] = None,
        publish_failure_to: Optional[str] = None,
    ):
        self._serializer = serializer
        if publish_all_to is not None and all(
            p is None for p in [publish_success_to, publish_failure_to]
        ):
            self.publish_success_to: str = publish_all_to
            self.publish_failure_to: str = publish_all_to
        elif (
            publish_success_to is not None and publish_failure_to is not None
        ) and publish_all_to is None:
            self.publish_success_to: str = publish_success_to
            self.publish_failure_to: str = publish_failure_to
        else:
            raise ValueError(
                """Provide "publish_all_to" only,
                 or else provide both "publish_success_to" and "publish_failure_to"""
            )

    @abstractmethod
    def publish_message(self, serialized_message: Any, to: str):
        raise NotImplementedError("No default implementation in base Publisher class")

    def _get_destination(self, status: HandlingResultStatus):
        if status == HandlingResultStatus.OK:
            return self.publish_success_to
        elif status == HandlingResultStatus.ERR:
            return self.publish_failure_to
        else:
            raise ValueError(f"Unknown status {status}")

    def _publish_serialized(self, data: Mapping[str, Any], to: str):
        serialized = self._serializer.serialize(data)
        self.publish_message(serialized, to)

    def publish_result(self, result: HandlingResult):
        data = result.data
        if data is None:
            return
        destination = self._get_destination(result.status)
        if isinstance(data, Mapping):
            self._publish_serialized(data, to=destination)
        elif isinstance(data, List):
            for item in data:
                self._publish_serialized(item, to=destination)
        else:
            raise ValueError("Invalid data structure")
