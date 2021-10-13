from typing import Optional
from functools import lru_cache

from core import config
from aioredis import Redis
from aiocache import RedisCache
from aiocache.serializers import PickleSerializer

redis: Optional[Redis] = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


@lru_cache()
def get_redis_cache_config(namespace="main", pool_min_size=5, pool_max_size=10):
    return {
        "cache": RedisCache,
        "serializer": PickleSerializer(),
        "endpoint": config.REDIS_HOST,
        "port": config.REDIS_PORT,
        "namespace": namespace,
        "pool_min_size": pool_min_size,
        "pool_max_size": pool_max_size,
    }
