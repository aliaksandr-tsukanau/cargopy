import logging
from typing import Optional, Union, Any, Mapping

import marshmallow
from happyly._deprecations.utils import will_be_removed

from happyly.logs.request_id import RequestIdLogger
from happyly.serialization import DUMMY_SERDE
from happyly.serialization.json import BinaryJSONSerializerForSchema
from ..subscribers import GooglePubSubSubscriber
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from happyly import Handler, Serializer
from happyly.listening.listener import ExecutorWithAck


_LOGGER = logging.getLogger(__name__)


def _format_message(message):
    return f'data: {message.data}, attributes: {message.attributes}'


class GooglePubSubExecutorWithRequestId(
    ExecutorWithAck[
        JSONDeserializerWithRequestIdRequired,
        Union[None, GooglePubSubPublisher],
        Serializer,
    ]
):
    """
    ExecutorWithAck subtype which adds advanced logging based on topic and request id.
    """

    def __init__(
        self,
        subscriber: GooglePubSubSubscriber,
        handler: Handler,
        deserializer: JSONDeserializerWithRequestIdRequired,
        serializer: BinaryJSONSerializerForSchema = None,
        publisher: Optional[GooglePubSubPublisher] = None,
        from_topic: str = '',
    ):
        self.from_topic = from_topic
        super().__init__(
            subscriber=subscriber,
            publisher=publisher,
            handler=handler,
            deserializer=deserializer,
            serializer=serializer if serializer is not None else DUMMY_SERDE,
        )

    def on_received(self, original_message: Any):
        logger = RequestIdLogger(_LOGGER, self.from_topic)
        logger.info(f"Received message: {_format_message(original_message)}")

    def on_deserialized(
        self, original_message: Any, deserialized_message: Mapping[str, Any]
    ):
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

    def on_handled(
        self, original_message: Any, deserialized_message: Mapping[str, Any], result
    ):
        assert self.deserializer is not None
        request_id = deserialized_message[self.deserializer.request_id_field]
        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f"Message handled, result {result}")

    def on_handling_failed(
        self,
        original_message: Any,
        deserialized_message: Mapping[str, Any],
        error: Exception,
    ):
        assert self.deserializer is not None
        request_id = deserialized_message[self.deserializer.request_id_field]
        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f'Failed to handle message, error {error}')

    def on_published(
        self,
        original_message: Any,
        deserialized_message: Optional[Mapping[str, Any]],
        result,
        serialized_message,
    ):
        assert self.deserializer is not None
        request_id = ''
        if deserialized_message is not None:
            request_id = deserialized_message[self.deserializer.request_id_field]

        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.info(f"Published serialized result: {serialized_message}")

    def on_publishing_failed(
        self,
        original_message: Any,
        deserialized_message: Optional[Mapping[str, Any]],
        result,
        serialized_message,
        error: Exception,
    ):
        assert self.deserializer is not None
        request_id = ''
        if deserialized_message is not None:
            request_id = deserialized_message[self.deserializer.request_id_field]

        logger = RequestIdLogger(_LOGGER, self.from_topic, request_id)
        logger.exception(f"Failed to publish result: {serialized_message}")

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


class _BaseGoogleListenerWithRequestIdLogger(GooglePubSubExecutorWithRequestId):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        will_be_removed(
            '_BaseGoogleListenerWithRequestIdLogger',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )


class GoogleBaseReceiver(_BaseGoogleListenerWithRequestIdLogger):
    def __init__(
        self,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        project: str,
        handler: Handler,
        from_topic: str = '',
    ):
        will_be_removed(
            'GoogleBaseReceiver',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )
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
        will_be_removed(
            'GoogleBaseReceiveAndReply',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )
        subscriber = GooglePubSubSubscriber(
            project=project, subscription_name=from_subscription
        )
        deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        serializer = BinaryJSONSerializerForSchema(schema=output_schema)
        publisher = GooglePubSubPublisher(project=project, to_topic=to_topic)
        super().__init__(
            handler=handler,
            deserializer=deserializer,
            subscriber=subscriber,
            serializer=serializer,
            publisher=publisher,
            from_topic=from_topic,
        )
