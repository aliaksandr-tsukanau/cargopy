from abc import ABC

from attr import attrs

from handling import Handler
from parsing.parser import Parser


@attrs(auto_attribs=True, frozen=True)
class Listener(ABC):
    handler: Handler
    parser: Parser

