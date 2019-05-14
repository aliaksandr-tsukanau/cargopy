import logging
import warnings

from happyly.caching.cacher import Cacher

_LOGGER = logging.getLogger(__name__)


class RedisCacher(Cacher):
    def __init__(self, host: str, port: int, prefix: str = ''):
        warnings.warn(
            'RedisCacher will be removed in happyly v0.11.0', DeprecationWarning
        )

        try:
            import redis
        except ImportError as e:
            raise ImportError('Please install redis>=3.0 to use this feature.') from e
        self.prefix = prefix
        self.client = redis.StrictRedis(host=host, port=port)
        _LOGGER.info(
            f'Cache was successfully initialized with Redis client ({host}:{port})'
        )
        if self.prefix != '':
            _LOGGER.info(f'Using prefix {self.prefix}')

    def add(self, data: str, key: str):
        self.client.hset(self.prefix, key, data)
        _LOGGER.info(f'Cached message with id {key}')

    def remove(self, key: str):
        self.client.hdel(self.prefix, key)
        _LOGGER.info(f'Message with id {key} was removed from cache')

    def get(self, key: str):
        self.client.hget(self.prefix, key)

    def get_all(self):
        keys = self.client.hkeys(self.prefix)
        return [self.client.hget(self.prefix, k) for k in keys]
