import logging

import backoff
import elasticsearch
import psycopg2
from psycopg2.extras import DictCursor
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from urllib3.exceptions import NewConnectionError


def backoff_hdlr(details):
    logging.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, (psycopg2.Error, psycopg2.OperationalError), on_backoff=backoff_hdlr)
def connect_to_postges(postgres_settings: dict) -> psycopg2.extensions.connection:
    pg_conn: psycopg2.extensions.connection = psycopg2.connect(**postgres_settings, cursor_factory=DictCursor)
    return pg_conn


@backoff.on_exception(backoff.expo, (ValueError, NewConnectionError), on_backoff=backoff_hdlr)
def connect_to_elastic(host: str) -> elasticsearch.client.Elasticsearch:
    es: elasticsearch.client.Elasticsearch = elasticsearch.Elasticsearch(host, verify_certs=True)
    if not es.ping():
        raise ValueError("Connection failed")
    return es


@backoff.on_exception(backoff.expo, (RedisConnectionError), on_backoff=backoff_hdlr)
def connect_to_redis(settings: dict) -> Redis:
    redis_adapter: Redis = Redis(**settings)
    redis_adapter.ping()
    return redis_adapter
