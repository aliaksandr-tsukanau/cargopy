from typing import Union, Optional, Any

import marshmallow

from ..high_level.base import GoogleBaseReceiveAndReply, GoogleBaseReceiver
from happyly.handling.dummy_handler import DUMMY_HANDLER
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from ..serializers import BinaryJSONSerializer
from happyly.handling import Handler
from happyly.listening.executor import Executor


class GoogleSimpleSender(
    Executor[Union[None, JSONDeserializerWithRequestIdRequired], GooglePubSubPublisher]
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
            publish_all_to=to_topic,
            serializer=BinaryJSONSerializer(schema=output_schema),
        )
        super().__init__(
            publisher=publisher, handler=handler, deserializer=deserializer
        )


class GoogleSimpleReceiver(GoogleBaseReceiver):
    def _after_on_received(self, message: Optional[Any]):
        super()._after_on_received(message)
        self.ack(message)


class GoogleSimpleReceiveAndReply(GoogleBaseReceiveAndReply):
    def _after_on_received(self, message: Optional[Any]):
        super()._after_on_received(message)
        self.ack(message)


# for compatibility
GoogleReceiveAndReplyComponent = GoogleSimpleReceiveAndReply
