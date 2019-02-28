from typing import Mapping, Any, Union, List

ParsedMessage = Mapping[str, Any]
ZeroToManyParsedMessages = Union[ParsedMessage, List[ParsedMessage], None]
