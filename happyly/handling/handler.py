from abc import ABC, abstractmethod
from typing import Mapping, Any, Optional

_no_base_impl = NotImplementedError('No default implementation in base Handler class')


class Handler(ABC):
    """
    A class containing logic to handle a parsed message.
    """

    @abstractmethod
    def handle(self, message: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        """
        Applies logic using a provided message,
        optionally gives back one or more results.
        Each result consists of message attributes which can be serialized and sent.
        When fails, calls :meth:`on_handling_failed`

        :param message: A parsed message as a dictionary of attributes

        :return: None if no result is extracted from handling,
            a dictionary of attributes for single result
        """
        raise _no_base_impl

    @abstractmethod
    def on_handling_failed(
        self, message: Mapping[str, Any], error: Exception
    ) -> Optional[Mapping[str, Any]]:
        """
        Applies fallback logic using a provided message
        when :meth:`handle` fails,
        optionally gives back one or more results.
        Enforces users of :class:`Handler` class
        to provide explicit strategy for errors.

        If you want to propagate error further to the underlying Executor/Handler,
        just re-raise an `error` here::

            def on_handling_failed(self, message, error):
                raise error

        :param message: A parsed message as a dictionary of attributes
        :param error: Error raised by :meth:`handle`
        :return: None if no result is extracted from handling,
            a dictionary of attributes for single result
        """
        raise _no_base_impl

    def __call__(self, message: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        try:
            return self.handle(message)
        except Exception as e:
            return self.on_handling_failed(message, e)
