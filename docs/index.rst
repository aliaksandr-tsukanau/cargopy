.. Happyly documentation master file, created by
   sphinx-quickstart on Wed Mar 27 22:16:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Happyly's documentation!
===================================

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

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   usecases
   installation
   concepts
   advanced
   apidoc


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
