from abc import ABC, abstractmethod
from typing import Mapping, Any

from .types import ZeroToManyParsedMessages
from .handling_result import HandlingResult

_no_base_impl = NotImplementedError('No default implementation in base Handler class')


class Handler(ABC):
    """
    A class containing logic to handle a parsed message.
    """

    @abstractmethod
    def handle(self, message: Mapping[str, Any]) -> ZeroToManyParsedMessages:
        """
        Applies logic using a provided message,
        optionally gives back one or more results.
        Each result consists of message attributes which can be serialized and sent.
        When fails, calls `on_handling_failed`

        :param message: A parsed message as a dictionary of attributes
        :return: None if no result is extracted from handling,
        a dictionary of attributes for single result
        or a list of dictionaries if handling provides multiple results
        """
        raise _no_base_impl

    @abstractmethod
    def on_handling_failed(
        self, message: Mapping[str, Any], error: Exception
    ) -> ZeroToManyParsedMessages:
        """
        Applies fallback logic using a provided message when `handle` fails,
        optionally gives back one or more results.
        Enforces users of `Handler` class to provide explicit strategy for errors

        :param message: A parsed message as a dictionary of attributes
        :param error: Error raised by `handle`
        :return: None if no result is extracted from handling,
        a dictionary of attributes for single result
        or a list of dictionaries if handling provides multiple results
        """
        raise _no_base_impl

    def __call__(self, message: Mapping[str, Any]) -> HandlingResult:
        try:
            result_data = self.handle(message)
            return HandlingResult.ok(result_data)
        except Exception as e:
            result_data = self.on_handling_failed(message, e)
            return HandlingResult.err(result_data)
