from abc import ABC, abstractmethod
from typing import Mapping, Any

from listening import Message


class Parser(ABC):

    @abstractmethod
    def parse(self, message: Message) -> Mapping[str, Any]:
        raise NotImplementedError('No default implementation in base Parser class')
