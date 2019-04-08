from typing import Union, Optional

import marshmallow

from happyly._deprecations.utils import will_be_removed
from .early_ack import GoogleEarlyAckReceiver, GoogleEarlyAckReceiveAndReply
from happyly.handling.dummy_handler import DUMMY_HANDLER
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from ..serializers import BinaryJSONSerializer
from happyly.handling import Handler
from happyly.listening.executor import Executor


class GoogleSimpleSender(
    Executor[
        Union[None, JSONDeserializerWithRequestIdRequired],
        GooglePubSubPublisher,
        BinaryJSONSerializer,
    ]
):
    def __init__(
        self,
        output_schema: marshmallow.Schema,
        to_topic: str,
        project: str,
        handler: Handler = DUMMY_HANDLER,
        input_schema: Optional[marshmallow.Schema] = None,
    ):
        if input_schema is None:
            deserializer = None
        else:
            deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        publisher = GooglePubSubPublisher(
            project=project,
            to_topic=to_topic,
        )
        serializer = BinaryJSONSerializer(schema=output_schema)
        super().__init__(
            publisher=publisher, handler=handler, deserializer=deserializer, serializer=serializer
        )


class GoogleSimpleReceiver(GoogleEarlyAckReceiver):
    def __init__(self, *args, **kwargs):
        will_be_removed('GoogleSimpleReceiver', GoogleEarlyAckReceiver, '0.8.0')
        super().__init__(*args, **kwargs)


class GoogleSimpleReceiveAndReply(GoogleEarlyAckReceiveAndReply):
    def __init__(self, *args, **kwargs):
        will_be_removed(
            'GoogleSimpleReceiveAndReply', GoogleEarlyAckReceiveAndReply, '0.8.0'
        )
        super().__init__(*args, **kwargs)


class GoogleReceiveAndReplyComponent(GoogleEarlyAckReceiveAndReply):
    def __init__(self, *args, **kwargs):
        will_be_removed(
            'GoogleReceiveAndReplyComponent', GoogleEarlyAckReceiveAndReply, '0.8.0'
        )
        super().__init__(*args, **kwargs)
