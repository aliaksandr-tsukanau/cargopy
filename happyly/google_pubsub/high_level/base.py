import logging
from typing import Optional, Union, Any, Mapping

import marshmallow

from happyly.logs.request_id import RequestIdLogger
from happyly.serialization.dummy import DummySerde
from serialization import DUMMY_SERDE
from ..subscribers import GooglePubSubSubscriber
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from ..serializers import BinaryJSONSerializer
from happyly import Handler, Serializer
from happyly.listening.listener import ListenerWithAck


_LOGGER = logging.getLogger(__name__)


def _format_message(message):
    return f'data: {message.data}, attributes: {message.attributes}'


class _BaseGoogleListenerWithRequestIdLogger(
    ListenerWithAck[
        JSONDeserializerWithRequestIdRequired,
        Union[None, GooglePubSubPublisher],
        Union[DummySerde, BinaryJSONSerializer],
    ]
):
    """
    Introduces advanced logging based on topic and request id.
    """

    def __init__(
        self,
        subscriber: GooglePubSubSubscriber,
        handler: Handler,
        deserializer: JSONDeserializerWithRequestIdRequired,
        serializer: Serializer = DUMMY_SERDE,
        publisher: Optional[GooglePubSubPublisher] = None,
        from_topic: str = '',
    ):
        self.from_topic = from_topic
        super().__init__(
            subscriber=subscriber,
            publisher=publisher,
            handler=handler,
            deserializer=deserializer,
            serializer=serializer,
        )

    def on_received(self, original_message: Any):
        logger = RequestIdLogger(_LOGGER, self.from_topic)
        logger.info(f"Received message: {_format_message(original_message)}")

    def on_deserialized(self, original_message: Any, deserialized_message: Mapping[str, Any]):
        assert self.deserializer is not None
        request_id = deserialized_message[self.deserializer.request_id_field]

        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.debug(
            f"Message successfully deserialized into attributes: {deserialized_message}"
        )

    def on_deserialization_failed(self, original_message: Any, error: Exception):
        logger = RequestIdLogger(_LOGGER, self.from_topic)
        logger.exception(
            f"Was not able to deserialize the following message: "
            f"{_format_message(original_message)}"
        )

    def on_handled(self, original_message: Any, deserialized_message: Mapping[str, Any], result):
        assert self.deserializer is not None
        request_id = deserialized_message[self.deserializer.request_id_field]
        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f"Message handled, status {result.status}")

    def on_handling_failed(self, original_message: Any, deserialized_message: Mapping[str, Any], error: Exception):
        assert self.deserializer is not None
        request_id = deserialized_message[self.deserializer.request_id_field]
        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f'Failed to handle message, error {error}')

    def on_published(self, original_message: Any, deserialized_message: Optional[Mapping[str, Any]],
                     result):
        assert self.deserializer is not None
        request_id = ''
        if deserialized_message is not None:
            request_id = deserialized_message[self.deserializer.request_id_field]

        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f"Published result: {result.data}")

    def on_publishing_failed(self, original_message: Any, deserialized_message: Optional[Mapping[str, Any]],
                             result, error: Exception):
        assert self.deserializer is not None
        request_id = ''
        if deserialized_message is not None:
            request_id = deserialized_message[self.deserializer.request_id_field]

        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.exception(f"Failed to publish result: {result.data}")

    def on_acknowledged(self, message: Any):
        assert self.deserializer is not None
        try:
            msg: Mapping = self.deserializer.deserialize(message)
            req_id = msg[self.deserializer.request_id_field]
        except Exception:
            req_id = ''
        logger = RequestIdLogger(_LOGGER, self.from_topic, req_id)
        logger.info('Message acknowledged.')

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        assert self.deserializer is not None
        try:
            msg: Mapping = self.deserializer.deserialize(original_message)
            req_id = msg[self.deserializer.request_id_field]
        except Exception:
            req_id = ''
        logger = RequestIdLogger(_LOGGER, self.from_topic, req_id)
        logger.info('Pipeline execution finished.')

    def on_stopped(self, original_message: Any, reason: str = ''):
        assert self.deserializer is not None
        try:
            msg: Mapping = self.deserializer.deserialize(original_message)
            req_id = msg[self.deserializer.request_id_field]
        except Exception:
            req_id = ''
        logger = RequestIdLogger(_LOGGER, self.from_topic, req_id)
        s = "." if reason == "" else f" due to the reason: {reason}."
        logger.info(f'Stopped pipeline{s}')


class GoogleBaseReceiver(_BaseGoogleListenerWithRequestIdLogger):
    def __init__(
        self,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        project: str,
        handler: Handler,
        from_topic: str = '',
    ):
        subscriber = GooglePubSubSubscriber(
            project=project, subscription_name=from_subscription
        )
        deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        super().__init__(
            subscriber=subscriber,
            handler=handler,
            deserializer=deserializer,
            from_topic=from_topic,
        )


class GoogleBaseReceiveAndReply(_BaseGoogleListenerWithRequestIdLogger):
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
        subscriber = GooglePubSubSubscriber(
            project=project, subscription_name=from_subscription
        )
        deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        serializer = BinaryJSONSerializer(schema=output_schema)
        publisher = GooglePubSubPublisher(
            project=project,
            to_topic=to_topic,
        )
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            subscriber=subscriber,
            serializer=serializer,
            publisher=publisher,
            from_topic=from_topic,
        )
