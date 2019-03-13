from enum import Enum

from attr import attrs

from .types import ZeroToManyParsedMessages


class HandlingResultStatus(Enum):
    OK = 'OK'
    ERR = 'ERR'


@attrs(auto_attribs=True, frozen=True)
class HandlingResult:
    status: HandlingResultStatus
    data: ZeroToManyParsedMessages

    @classmethod
    def ok(cls, data):
        return HandlingResult(status=HandlingResultStatus.OK, data=data)

    @classmethod
    def err(cls, data):
        return HandlingResult(status=HandlingResultStatus.ERR, data=data)
