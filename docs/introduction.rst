Introduction
============

Happyly is a scalable solution for systems which handle any kind of messages.

Happyly helps to abstract your business logic from messaging stuff,
so that your code is maintainable and ensures separation of concerns.

Have you ever seen a codebase where serialization,
message queue managing and business logic
are mixed together like a spaghetti? I have.
Imagine switching between Google Pub/Sub and Django REST Framework. Or Celery.
This shouldn't be a nightmare but it often is.

Here's the approach of Happyly:

* Write you business logic in universal *Handlers*,
  which don't care at all how you serialize things or send them over network etc.
* Describe your schemas using ORM/Framework-agnostic technology.
* Plug-in any details of messaging protocol, serialization and networking.
  Change them with different drop-in replacements at any time.

Happyly can be used with Flask, Celery, Django, Kafka or whatever
technology which can be used for messaging
and also provides first-class support of Google Pub/Sub.


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

    def handle_my_stuff(message: dict):
        try:
            return process_things(message['ID'])
        except NeedToRetry as error:
            raise error from error
        except Exception:
            _LOGGER.error('An error occured')

  :code:`handle_my_stuff` is now also usable with Celery or Flask.
  Or with yaml serialization.
  Or with :code:`message.attributes` instead of :code:`message.data`.
  Without any change.

* You are going to **change messaging technology** later.

  Let's say you are prototyping your project with Flask
  and are planning to move to Celery for better fault tolerance then.
  Or to Google Pub/Sub. You just haven't decided yet.

  Easy! Here's how Happyly can help.

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

    def handle_things(message: dict):
        try:
            req_id = message['request_id']
            if req_id in ALLOWED:
                result = get_result_for_id(req_id)
            else:
                result = 'not allowed'
            return {
                'request_id': req_id
                'result': result
            }
        except Exception as error:
            return {
                'request_id': message['request_id']
                'result': 'error',
                'error': str(error)
            }

  3. Plug it into Flask:

  .. code-block:: python

    @app.route('/')
    def root():
        executor = happyly.Executor(
            handler=handle_things,
            deserializer=happyly.serialization.JSONDeserializerForSchema(
                schema=MyInputSchema()
            ),
            serializer=happyly.serialization.flask.JsonifyForSchema(
                schema=MyOutputSchema()
            ),
        )
        request_data = request.get_json()
        return executor.run_for_result(request_data)


  3. Painlessly switch to Celery when you need:

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

  4. Or to Google Pub/Sub:

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
