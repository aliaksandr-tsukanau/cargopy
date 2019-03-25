import logging

import redis

from happyly.caching.cacher import Cacher


_LOGGER = logging.getLogger(__name__)


class RedisCacher(Cacher):
    def __init__(self, host: str, port: int, prefix: str = ''):
        self.prefix = prefix
        self.client = redis.StrictRedis(host=host, port=port)
        _LOGGER.info(
            f'Cache was successfully initialized with Redis client ({host}:{port})'
        )
        if self.prefix != '':
            _LOGGER.info(f'Using prefix {self.prefix}')

    def add(self, data: str, key: str):
        full_key = f'{self.prefix}{key}'
        self.client.set(full_key, data)
        _LOGGER.info(f'Cached message with id {key}')

    def remove(self, key: str):
        full_key = f'{self.prefix}{key}'
        self.client.delete(full_key)
        _LOGGER.info(f'Message with id {key} was removed from cache')

    def get(self, key: str):
        full_key = f'{self.prefix}{key}'
        self.client.get(full_key)

    def get_all(self):
        keys: str = self.client.keys()
        return [self.client.get(k) for k in keys if k.startswith(self.prefix)]
