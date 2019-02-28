from abc import ABC
from typing import Mapping, Any

from attr import attrs

from handling import Handler
from parsing.parser import Parser


@attrs(auto_attribs=True, frozen=True)
class Listener(ABC):
    handler: Handler
    parser: Parser
    subscriber: Subscriber

    def on_received(self, message: Message):
        pass

    def on_acknowledged(self, message: Message):
        pass

    def on_parsed(self, original: Message, parsed: Mapping[str, Any]):
        pass

    def on_parsing_failed(self, message: Message, error: Exception):
        raise error

