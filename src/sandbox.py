import os
from typing import Mapping, Any, Callable

from google.cloud import pubsub_v1

from handling import Handler
from handling.types import ParsedMessage, ZeroToManyParsedMessages
from listening import Listener, Message
from parsing import Parser
from subscribing import Subscriber


class DummyHandler(Handler):

    def handle(self, message: ParsedMessage) -> ZeroToManyParsedMessages:
        print(message)
        return None

    def on_handling_failed(self, message: ParsedMessage, error: Exception) -> ZeroToManyParsedMessages:
        raise error


class DummyParser(Parser):

    def parse(self, message: Message) -> Mapping[str, Any]:
        return message.attributes['request_id']


class DummySubscriber(Subscriber):

    def subscribe(self, callback: Callable[[Message], Any]):
        s = pubsub_v1.SubscriberClient()
        return s.subscribe('projects/machinaseptember2016/subscriptions/happyly_testing_01', callback=callback)


if __name__ == '__main__':
    SERVICE_ACCOUNT_FILE = '/cfg/machinaseptember2016-60ec1dc9f2ae.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

    li = Listener(
        handler=DummyHandler(),
        parser=DummyParser(),
        subscriber=DummySubscriber()
    )
    future = li.start_listening()
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()

