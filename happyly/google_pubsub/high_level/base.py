import marshmallow

from ..subscribers import GooglePubSubSubscriber
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from ..serializers import BinaryJSONSerializer
from happyly import Handler
from happyly.listening.listener import ListenerWithAck


class GoogleBaseReceiver(ListenerWithAck[JSONDeserializerWithRequestIdRequired, None]):
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


class GoogleBaseReceiveAndReply(
    ListenerWithAck[JSONDeserializerWithRequestIdRequired, GooglePubSubPublisher]
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
