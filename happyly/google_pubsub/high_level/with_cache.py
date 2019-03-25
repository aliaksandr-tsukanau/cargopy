import marshmallow

from happyly.caching.cacher import Cacher
from happyly.caching.mixins import CacheByRequestIdMixin
from happyly.handling import Handler
from .simple import GoogleSimpleReceiveAndReply, GoogleSimpleReceiver


class GoogleCachedReceiveAndReply(CacheByRequestIdMixin, GoogleSimpleReceiveAndReply):
    def __init__(
        self,
        handler: Handler,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        from_topic: str,
        output_schema: marshmallow.Schema,
        to_topic: str,
        project: str,
        cacher: Cacher,
    ):
        self.from_topic = from_topic
        GoogleSimpleReceiveAndReply.__init__(
            self,
            handler,
            input_schema,
            from_subscription,
            output_schema,
            to_topic,
            project,
        )
        CacheByRequestIdMixin.__init__(self, cacher)


class GoogleCachedReceiver(CacheByRequestIdMixin, GoogleSimpleReceiver):
    def __init__(
        self,
        handler: Handler,
        input_schema: marshmallow.Schema,
        from_subscription: str,
        from_topic: str,
        project: str,
        cacher: Cacher,
    ):
        self.from_topic = from_topic
        GoogleSimpleReceiver.__init__(
            self, input_schema, from_subscription, project, handler
        )
        CacheByRequestIdMixin.__init__(self, cacher)
