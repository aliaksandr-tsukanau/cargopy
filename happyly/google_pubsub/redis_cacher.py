import logging
from typing import Any

import redis

from happyly.caching.cacher import Cacher


_LOGGER = logging.getLogger(__name__)


class RedisCacher(Cacher):
    def __init__(self, host, port):
        self.client = redis.StrictRedis(host=host, port=port)
        _LOGGER.info(
            f'Cache was successfully initialized with Redis client ({host}:{port})'
        )

    def add(self, message: Any, key: str):
        self.client.set(key, message.data)
        _LOGGER.info(f'Cached message with id {key}')

    def remove(self, key: str):
        self.client.delete(key)
        _LOGGER.info(f'Message with id {key} was removed from cache')

    def get(self, key: str):
        self.client.get(key)

    def get_all(self):
        keys = self.client.keys()
        return [self.client.get(k) for k in keys]
