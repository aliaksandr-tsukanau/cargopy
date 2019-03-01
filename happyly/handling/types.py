from typing import Mapping, Any, Union, List

_ParsedMessage = Mapping[str, Any]
ZeroToManyParsedMessages = Union[_ParsedMessage, List[_ParsedMessage], None]
