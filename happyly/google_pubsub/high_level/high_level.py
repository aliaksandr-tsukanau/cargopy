from typing import Mapping, Any

import marshmallow

from happyly.google_pubsub.deserializers import JSONDeserializerWithRequestIdRequired
from happyly.google_pubsub.publishers import GooglePubSubPublisher
from happyly.google_pubsub.serializers import BinaryJSONSerializer
from happyly.google_pubsub.subscribers import GooglePubSubSubscriber
from happyly.handling import Handler
from happyly.listening import Listener
from happyly.listening.executor import Executor


class GoogleSimpleSender(Executor):

    def __init__(self,
                 handler: Handler,
                 output_schema: marshmallow.Schema,
                 to_topic: str,
                 project: str,
                 ):
        publisher = GooglePubSubPublisher(
            project=project,
            publish_all_to=to_topic,
            serializer=BinaryJSONSerializer(
                schema=output_schema,
            )
        )
        handler = handler
        super().__init__(publisher=publisher, handler=handler)


class GoogleSimpleReceiver(Listener):

    def __init__(self,
                 handler: Handler,
                 input_schema: marshmallow.Schema,
                 from_subscription: str,
                 project: str,
                 ):
        subscriber = GooglePubSubSubscriber(
            project=project,
            subscription_name=from_subscription,
        )
        handler = handler
        deserializer = JSONDeserializerWithRequestIdRequired(
            schema=input_schema,
        )
        super().__init__(subscriber=subscriber, handler=handler, deserializer=deserializer)


class GoogleReceiveAndReplyComponent(Listener):

    def __init__(self,
                 handler: Handler,
                 input_schema: marshmallow.Schema,
                 from_subscription: str,
                 output_schema: marshmallow.Schema,
                 to_topic: str,
                 project: str,
                 ):
        subscriber = GooglePubSubSubscriber(
            project=project,
            subscription_name=from_subscription,
        )
        handler = handler
        deserializer = JSONDeserializerWithRequestIdRequired(
            schema=input_schema,
        )
        publisher = GooglePubSubPublisher(
            project=project,
            publish_all_to=to_topic,
            serializer=BinaryJSONSerializer(
                schema=output_schema,
            )
        )
        super().__init__(handler=handler, deserializer=deserializer, subscriber=subscriber, publisher=publisher)
