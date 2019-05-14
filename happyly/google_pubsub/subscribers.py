import logging
from typing import Callable, Any

from happyly.pubsub import SubscriberWithAck


_LOGGER = logging.getLogger(__name__)


class GooglePubSubSubscriber(SubscriberWithAck):
    def __init__(self, project: str, subscription_name: str):
        try:
            from google.cloud import pubsub_v1
        except ImportError:
            raise ImportError(
                'Please install google-cloud-pubsub to use this component'
            )

        super().__init__()
        self.project = project
        self.subscription_name = subscription_name
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
