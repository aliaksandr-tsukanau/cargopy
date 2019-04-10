import logging

from marshmallow import fields

import happyly
from happyly import Executor
from happyly.serialization.json import JSONDeserializerForSchema

logging.basicConfig(level=logging.INFO)


class MySchema(happyly.Schema):
    request_id = fields.Str(required=True)
    label = fields.Int(required=True)
    extra = fields.Str()  # not required


def handle_my_stuff(message: dict):
    print(message['label'])


if __name__ == '__main__':
    Executor(
        handler=handle_my_stuff,
        deserializer=JSONDeserializerForSchema(schema=MySchema()),
    ).run('{"request_id": "123", "label": 4}')
