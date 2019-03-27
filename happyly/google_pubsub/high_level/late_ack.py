from typing import Optional, Any

from ..high_level.base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleLateAckReceiver(GoogleBaseReceiver):
    def run(self, message: Optional[Any] = None):
        super().run(message)
        self.ack(message)


class GoogleLateAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def run(self, message: Optional[Any] = None):
        super().run(message)
        self.ack(message)
