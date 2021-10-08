import logging

import aioredis
import backoff
from core import config
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError

from db import elastic, redis


def backoff_hdlr(details):
    logging.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, (ConnectionRefusedError), on_backoff=backoff_hdlr, max_tries=10)
async def init_redis_connection():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    )


@backoff.on_exception(backoff.expo, (ConnectionError), on_backoff=backoff_hdlr, max_tries=10)
async def init_elasticsearch_connection():
    elastic.es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}"])


@backoff.on_exception(backoff.expo, (ConnectionRefusedError), on_backoff=backoff_hdlr)
async def init_connectons():
    await init_redis_connection()
    await init_elasticsearch_connection()
    # redis.redis = await aioredis.create_redis_pool(
    #     (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    # )
    # elastic.es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}"])


async def close_connections():
    await redis.redis.close()
    await elastic.es.close()
