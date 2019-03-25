from typing import Union, Optional

import marshmallow

from happyly.handling.dummy_handler import DUMMY_HANDLER
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from ..serializers import BinaryJSONSerializer
from ..subscribers import GooglePubSubSubscriber
from happyly.handling import Handler
from happyly.listening.executor import Executor
from happyly.listening.listener import EarlyAckListener


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


class GoogleSimpleReceiver(
    EarlyAckListener[JSONDeserializerWithRequestIdRequired, None]
):
    def __init__(
        self,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        project: str,
        handler: Handler,
        from_topic: str = '',
    ):
        self.from_topic = from_topic
        subscriber = GooglePubSubSubscriber(
            project=project, subscription_name=from_subscription
        )
        deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        super().__init__(
            subscriber=subscriber, handler=handler, deserializer=deserializer
        )


class GoogleSimpleReceiveAndReply(
    EarlyAckListener[JSONDeserializerWithRequestIdRequired, GooglePubSubPublisher]
):
    def __init__(
        self,
        handler: Handler,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        output_schema: marshmallow.Schema,
        to_topic: str,
        project: str,
        from_topic: str = '',
    ):
        self.from_topic = from_topic
        subscriber = GooglePubSubSubscriber(
            project=project, subscription_name=from_subscription
        )
        deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        publisher = GooglePubSubPublisher(
            project=project,
            publish_all_to=to_topic,
            serializer=BinaryJSONSerializer(schema=output_schema),
        )
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            subscriber=subscriber,
            publisher=publisher,
        )


# for compatibility
GoogleReceiveAndReplyComponent = GoogleSimpleReceiveAndReply
