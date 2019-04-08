from typing import Any

from google.cloud import pubsub_v1

from happyly.pubsub import BasePublisher


class GooglePubSubPublisher(BasePublisher):
    def publish(self, serialized_message: Any):
        future = self._publisher_client.publish(
            f'projects/{self.project}/topics/{self.to_topic}', serialized_message
        )
        try:
            future.result()
            return
        except Exception as e:
            raise e

    def __init__(self, project: str, to_topic: str):
        super().__init__()
        self.project = project
        self.to_topic = to_topic
        self._publisher_client = pubsub_v1.PublisherClient()
