from typing import Union, Optional

import marshmallow
from happyly._deprecations.utils import will_be_removed

from happyly.handling.dummy_handler import DUMMY_HANDLER
from ..deserializers import JSONDeserializerWithRequestIdRequired
from ..publishers import GooglePubSubPublisher
from happyly.serialization.json import BinaryJSONSerializerForSchema
from happyly.handling import Handler
from happyly.listening.executor import Executor


class GoogleSimpleSender(
    Executor[
        Union[None, JSONDeserializerWithRequestIdRequired],
        GooglePubSubPublisher,
        BinaryJSONSerializerForSchema,
        None,
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
        will_be_removed(
            deprecated_name='GoogleSimpleSender',
            use_instead='ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            removing_in_version='0.11.0',
        )
        if input_schema is None:
            deserializer = None
        else:
            deserializer = JSONDeserializerWithRequestIdRequired(schema=input_schema)
        publisher = GooglePubSubPublisher(project=project, to_topic=to_topic)
        serializer = BinaryJSONSerializerForSchema(schema=output_schema)
        super().__init__(
            publisher=publisher,
            handler=handler,
            deserializer=deserializer,
            serializer=serializer,
        )
