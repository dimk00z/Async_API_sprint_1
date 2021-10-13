import logging

import backoff
import aioredis
from core import config
from db import redis, elastic
from elasticsearch import AsyncElasticsearch


def backoff_hdlr(details):
    logging.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, (Exception,), on_backoff=backoff_hdlr, max_tries=10)
async def init_redis_connection():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    )


@backoff.on_exception(backoff.expo, (Exception,), on_backoff=backoff_hdlr, max_tries=10)
async def init_elasticsearch_connection():
    elastic.es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}"])
    pong = await elastic.es.ping()
    if not pong:
        raise ConnectionError("Error connecting to Elastic!")


async def init_connectons():
    await init_redis_connection()
    await init_elasticsearch_connection()


async def close_connections():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()
