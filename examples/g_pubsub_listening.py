import logging
import os

from marshmallow import fields

import happyly
from google_pubsub import GoogleLateAckReceiver


class MySchema(happyly.Schema):
    request_id = fields.Str(required=True)


logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/cfg/creds.json'
    future = GoogleLateAckReceiver(
        handler=lambda msg: print(msg),
        from_topic='happyly_testing',
        from_subscription='happyly_testing_01',
        project=os.environ['PROJECT'],
        input_schema=MySchema(),
    ).start_listening()
    future.result()
