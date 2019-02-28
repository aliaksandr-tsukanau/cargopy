from abc import abstractmethod, ABC


class Message(ABC):

    @abstractmethod
    def ack(self):
        pass
