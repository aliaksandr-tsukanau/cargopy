from typing import Callable

from attr import attrs

from listening import Listener, Message


@attrs(auto_attribs=True, frozen=True)
class ListenerWithRequestIdRequired(Listener):
    get_request_id: Callable[[Message], str]
