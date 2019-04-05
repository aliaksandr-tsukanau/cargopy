Introduction
============

Happyly is a scalable solution for systems which handle any kind of messages.
Have you ever seen a codebase where serialization, acknowledgement and business logic
are mixed together like a spaghetti? I have.
Imagine switching between Google Pub/Sub and Django REST Framework. Or Celery.
This shouldn't be a nightmare but it often is.

Here's the approach of Happyly:

* Write you business logic in universal *Handlers*,
  which don't care at all how you serialize things or send them over network
  or deal with message queues.
* Describe your schemas using ORM/Framework-agnostic technology.
* Plug-in any details of messaging protocol, serialization and networking.
  Change them with different drop-in replacements at any time.


Use cases
---------

* **Google Pub/Sub**

  Let's be honest, the official
  `Python client library <https://googleapis.github.io/google-cloud-python/latest/pubsub/>`_
  is too low-level.
  You must serialize and deserialize things manually,
  as well as to `ack` and `nack` messages.

  Usual way:

  .. code-block:: python

    def callback(message):
        attributes = json.loads(message.data)
        try:
            result = process_things(attributes['ID'])    
            encoded = json.dumps(result).encode('utf-8')
            PUBLISHER.publish(TOPIC, encoded)
        except NeedToRetry:
            _LOGGER.info('Not acknowledging, will retry later.')
        except Exception:
            _LOGGER.error('An error occured')
            message.ack()
        else:
            message.ack()

  Happyly way:

  .. code-block:: python

    class MyHandler(happyly.handler):
        def handle(attributes: dict):
            return process_things(attributes['ID'])

        def on_handling_failed(attributes: dict, error):
            if isinstance(error, NeedToRetry):
                raise error from error
            else:
                _LOGGER.error('An error occured')

  :code:`MyHandler` is now also usable with Celery or Flask.
  Or with yaml serialization.
  Or with :code:`message.attributes` instead of :code:`message.data`.
  Without any change.

* You are going to **change messaging technology** later.

  Easy! Here's an example.

  1. Define your message schemas.

  .. code-block:: python

      class MyInputSchema(happyly.Schema):
          request_id = marshmallow.fields.Str(required=True)

      class MyOutputSchema(happyly.Schema):
          request_id = marshmallow.fields.Str(required=True)
          result = marshmallow.fields.Str(required=True)
          error = marshmallow.fields.Str()

  2. Define your handler

  .. code-block:: python

    class ProcessThings(happyly.Handler):
        def handle(message: dict):
            req_id = message['request_id']
            if req_id in ALLOWED:
                result = get_result_for_id(req_id)
            else:
                result = 'not allowed'
            return {
                'request_id': req_id
                'result': result
            }

        def on_handling_failed(message: dict, error):
            return {
                'request_id': message['request_id']
                'result': 'error',
                'error': str(error)
            }

  3. Plug it into Celery:

  .. code-block:: python

    @celery.task('hello')
    def hello(message):
        result = happyly.Executor(
            handler=ProcessThings(),
            serializer=happyly.DummyValidator(schema=MyInputSchema()),
            deserializer=happyly.DummyValidator(schema=MyOutputSchema()),
        ).run_for_result(
            message
        )
        return result

  4. Or Google Pub/Sub:

  .. code-block:: python

    happyly.Listener(
        handler=ProcessThings(),
        deserializer=happyly.google_pubsub.JSONDeserializerWithRequestIdRequired(
            schema=MyInputSchema()
        ),
        serializer=happyly.google_pubsub.BinaryJSONSerializer(
            schema=MyOutputSchema()
        ),
        publisher=happyly.google_pubsub.GooglePubSubPublisher(
            topic='my_topic',
            project='my_project',
        ),
     ).start_listening()

  5. Move to any other technology. Or swap serializer to another.
  Do whatever you need while your handler and schemas remain absolutely the same.
