from typing import Mapping, List

from happyly.handling.types import ZeroToManyParsedMessages
from .serializer import Serializer


def serialize_with_dispatching(
    serializer: Serializer, result_data: ZeroToManyParsedMessages
):
    if result_data is None:
        return None
    elif isinstance(result_data, Mapping):
        return serializer.serialize(result_data)
    elif isinstance(result_data, List):
        return [serializer.serialize(x) for x in result_data]
    else:
        raise TypeError('Invalid data structure')
