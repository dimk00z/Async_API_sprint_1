import logging
from os import environ
from time import sleep
from datetime import datetime

import psycopg2
import elasticsearch
from redis import Redis
from dotenv import load_dotenv
from loader.indexes import INDEXES
from loader.loader import ESLoader
from state import State, RedisStorage
from setting_loaders import load_etl_settings
from correct_terminate import TerminateProtected
from connections import connect_to_redis, connect_to_elastic, connect_to_postges
from transformers import (
    BaseTransformer,
    GenresTransformer,
    MoviesTransformer,
    PersonTransformer,
)
from extractors import (
    BaseExtractor,
    GenresPostgresExtractor,
    MoviesPostgresExtractor,
    PersonsPostgresExtractor,
)

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)
load_dotenv()


def proccess_index_etl(
    pg_conn,
    es_loader: ESLoader,
    extactor: BaseExtractor,
    tranformer: BaseTransformer,
    last_state: str,
    state: State,
    index: str,
):
    extractor: BaseExtractor = extactor(
        pg_conn=pg_conn,
        cursor_limit=int(environ.get("POSTGRES_PAGE_LIMIT")),
        last_state=last_state,
    )
    loaded_rows_number: int = 0

    for extracted_data in extractor.extract_data():
        transformer = tranformer(extracted_data=extracted_data)
        transformed_data: list[dict] = transformer.transform_data()
        loaded_rows_number = len(transformed_data)
        es_loader.bulk_index(
            transformed_data=transformed_data, last_state=last_state, index_name=index
        )
        state.set_state(f"{index}_updated_at", extracted_data[-1].updated_at)
        logging.info("Loaded %d %s to Elasticsearch", loaded_rows_number, index)
    if loaded_rows_number == 0:
        logging.info("There no %s for ETL", index)


def start_etl(pg_conn, es_loader: ESLoader, state: State):
    states: dict[str, str] = {
        "movies_updated_at": state.get_state("movies_updated_at"),
        "genres_updated_at": state.get_state("genres_updated_at"),
        "persons_updated_at": state.get_state("persons_updated_at"),
    }
    indexes = {
        "movies": {
            "extactor": MoviesPostgresExtractor,
            "tranformer": MoviesTransformer,
        },
        "genres": {
            "extactor": GenresPostgresExtractor,
            "tranformer": GenresTransformer,
        },
        "persons": {
            "extactor": PersonsPostgresExtractor,
            "tranformer": PersonTransformer,
        },
    }
    for index in indexes:
        proccess_index_etl(
            pg_conn=pg_conn,
            es_loader=es_loader,
            Extactor=indexes[index]["extactor"],
            Tranformer=indexes[index]["tranformer"],
            last_state=states[f"{index}_updated_at"],
            state=state,
            index=index,
        )


def create_es_indexes(elastic_settings):

    es: elasticsearch.client.Elasticsearch = connect_to_elastic(elastic_settings.host)
    es_loader = ESLoader(es=es, indexes=INDEXES)
    es_loader.drop_indexes()
    es_loader.create_indexes()
    es.transport.close()


def main():
    logging.info("Start etl_app at %s", datetime.now())

    postgres_settings, elastic_settings, redis_settings = load_etl_settings()

    repeat_time = int(environ.get("REPEAT_TIME"))

    redis_db: str = environ.get("REDIS_DB")
    redis_adapter: Redis = connect_to_redis(redis_settings.dict())

    if environ.get("ES_SHOULD_DROP_INDEX") == "TRUE":
        create_es_indexes(elastic_settings)
        redis_adapter.flushdb(redis_db)

    pg_conn: psycopg2.extensions.connection = connect_to_postges(postgres_settings.dict())
    state = State(storage=RedisStorage(redis_adapter=redis_adapter, redis_db=redis_db))
    es: elasticsearch.client.Elasticsearch = connect_to_elastic(elastic_settings.host)
    es_loader = ESLoader(es, indexes=INDEXES)

    with TerminateProtected(pg_conn=pg_conn, es=es):
        while True:
            start_etl(pg_conn=pg_conn, es_loader=es_loader, state=state)
            logging.info("Script is waiting %d seconds for restart", repeat_time)
            sleep(repeat_time)


if __name__ == "__main__":
    main()
