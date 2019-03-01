import logging
import os
from collections import namedtuple

import marshmallow
from marshmallow import fields

from happyly.google_pubsub.deserializers import JSONDeserializerWithRequestIdRequired
from happyly.google_pubsub.publishers import GooglePubSubPublisher
from happyly.google_pubsub.serializers import BinaryJSONSerializer
from happyly.handling import Handler
from happyly.listening.executor import Executor


class InputSchema(marshmallow.Schema):
    request_id = fields.Str(required=True)


class OutputSchema(marshmallow.Schema):
    request_id = fields.Str(required=True)
    code = fields.Int(required=True)


class MyHandler(Handler):

    def handle(self, message):
        print('Super heavy processing here......')
        return {
            'request_id': message['request_id'],
            'code': 123,
        }

    def on_handling_failed(self, message, error: Exception):
        print(repr(error))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    SERVICE_ACCOUNT_FILE = '/cfg/machinaseptember2016-60ec1dc9f2ae.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

    deserializer = JSONDeserializerWithRequestIdRequired(InputSchema(strict=True))
    serializer = BinaryJSONSerializer(OutputSchema(strict=True))

    listener = Executor(
        handler=MyHandler(),
        deserializer=deserializer,
        publisher=GooglePubSubPublisher(
            serializer=serializer,
            publish_all_to='happyly_testing',
            project='machinaseptember2016',
        )
    )
    msg = namedtuple('MessageMock', 'data')(b'{"request_id": "123"}')
    listener.run(msg)
