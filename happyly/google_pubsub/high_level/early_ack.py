from typing import Optional, Any

from .base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleEarlyAckReceiver(GoogleBaseReceiver):
    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)


class GoogleEarlyAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def _fetch_deserialized_and_result(self, message: Optional[Any]):
        self.ack(message)
        super()._fetch_deserialized_and_result(message)
