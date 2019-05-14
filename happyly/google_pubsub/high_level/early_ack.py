from typing import Optional, Any

from happyly._deprecations.utils import will_be_removed

from .base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleEarlyAckReceiver(GoogleBaseReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        will_be_removed(
            'GoogleEarlyAckReceiver',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )

    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)


class GoogleEarlyAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        will_be_removed(
            'GoogleEarlyAckReceiveAndReply',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )

    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)
