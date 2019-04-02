from enum import Enum

from attr import attrs

from .types import ZeroToManyParsedMessages


class HandlingResultStatus(Enum):
    """
    Handling status: `OK` or `ERR`
    """

    OK = 'OK'
    ERR = 'ERR'


@attrs(auto_attribs=True, frozen=True)
class HandlingResult:
    status: HandlingResultStatus
    """
    Status of message handling.
    """
    data: ZeroToManyParsedMessages
    """
    Result or results of handling.
    """

    @classmethod
    def ok(cls, data: ZeroToManyParsedMessages) -> 'HandlingResult':
        """
        Construct successful :class:`.HandlingResult`.

        :param data: message or list of messages which were processed.
        """
        return HandlingResult(status=HandlingResultStatus.OK, data=data)

    @classmethod
    def err(cls, data: ZeroToManyParsedMessages) -> 'HandlingResult':
        """
        Construct failed :class:`.HandlingResult`.

        :param data: message or list of messages which were processed.
        """
        return HandlingResult(status=HandlingResultStatus.ERR, data=data)
