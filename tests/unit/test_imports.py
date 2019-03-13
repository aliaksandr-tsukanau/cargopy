# flake8: noqa F401
def test_imports():
    import happyly

    import happyly.handling
    import happyly.listening
    import happyly.pubsub
    import happyly.serialization
    import happyly.google_pubsub

    from happyly.handling import Handler, HandlingResult, HandlingResultStatus
    from happyly.listening import Executor, Listener
    from happyly.pubsub import Publisher, Subscriber
    from happyly.serialization import Deserializer, Serializer

    from happyly.google_pubsub import (
        GoogleSimpleReceiver, GoogleSimpleSender, GoogleReceiveAndReplyComponent
    )
    from happyly.google_pubsub.deserializers import JSONDeserializerWithRequestIdRequired
    from happyly.google_pubsub.serializers import BinaryJSONSerializer
    from happyly.google_pubsub.publishers import GooglePubSubPublisher
    from happyly.google_pubsub.subscribers import GooglePubSubSubscriber
