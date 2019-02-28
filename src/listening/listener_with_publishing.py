from attr import attrs

from handling import HandlingResult
from listening import Listener
from publishing.publisher import Publisher


@attrs(auto_attribs=True)
class ListenerWithPublishing(Listener):
    publisher: Publisher

    def on_published(self, result: HandlingResult):
        pass

    def on_publishing_failed(self, result: HandlingResult, error: Exception):
        pass

    def on_handled(self, result: HandlingResult):
        super().on_handled(result)
        try:
            self.publisher.publish(result)
            self.on_published(result)
        except Exception as e:
            self.on_publishing_failed(result, error=e)
