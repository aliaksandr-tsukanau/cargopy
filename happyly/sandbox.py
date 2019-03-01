import json
import os
from typing import Mapping, Any

from google_pubsub.subscribers import GooglePubSubSubscriber
from happyly.handling import Handler
from happyly.listening import Listener
from happyly.handling.types import ParsedMessage
from happyly.serialization import Deserializer


class MyDeserializer(Deserializer):

    def deserialize(self, message):
        return json.loads(message)

    def build_error_result(self, message, error) -> Mapping[str, Any]:
        return {'error': repr(error)}


class MyHandler(Handler):

    def handle(self, message: ParsedMessage):
        print(f'Received message with {len(message)} attributes')
        print(f'request id is {message["request_id"]}')

    def on_handling_failed(self, _: ParsedMessage, error: Exception):
        print(repr(error))


if __name__ == '__main__':
    SERVICE_ACCOUNT_FILE = '/cfg/machinaseptember2016-60ec1dc9f2ae.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

    listener = Listener(
        handler=MyHandler(),
        deserializer=MyDeserializer(),
        subscriber=GooglePubSubSubscriber(
            project='machinaseptember2016',
            subscription_name='happyly_testing_01'
        )
    )
    future = listener.start_listening()
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
