from abc import ABC, abstractmethod
from typing import Mapping, Any, Union, List

from .handler_result import HandlingResult

AbstractMessage = Mapping[str, Any]
ZeroToManyMessages = Union[AbstractMessage, List[AbstractMessage], None]


_no_base_impl = NotImplementedError(f'No default implementation in base Handler class')


class Handler(ABC):

    @abstractmethod
    def handle(self, message: AbstractMessage) -> ZeroToManyMessages:
        raise _no_base_impl

    @abstractmethod
    def on_handling_failed(self, message: AbstractMessage, error: Exception) -> ZeroToManyMessages:
        raise _no_base_impl

    def __call__(self, message: AbstractMessage) -> HandlingResult:
        try:
            result_data = self.handle(message)
            return HandlingResult.ok(result_data)
        except Exception as e:
            result_data = self.on_handling_failed(message, e)
            return HandlingResult.err(result_data)
