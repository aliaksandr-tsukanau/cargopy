import logging
from typing import Callable, Any

from attr import attrs, attrib
from google.cloud import pubsub_v1

from happyly.pubsub import SubscriberWithAck


_LOGGER = logging.getLogger(__name__)


@attrs(auto_attribs=True)
class GooglePubSubSubscriber(SubscriberWithAck):
    project: str
    subscription_name: str
    _subscription_client: pubsub_v1.SubscriberClient = attrib(init=False)
    _subscription_path: str = attrib(init=False)

    def __attrs_post_init__(self):
        s = pubsub_v1.SubscriberClient()
        self._subscription_path = s.subscription_path(
            self.project, self.subscription_name
        )
        self._subscription_client = s

    def subscribe(self, callback: Callable[[Any], Any]):
        _LOGGER.info(f'Starting to listen to {self.subscription_name}')
        return self._subscription_client.subscribe(self._subscription_path, callback)

    def ack(self, message):
        message.ack()
