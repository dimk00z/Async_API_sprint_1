import logging
from typing import List

import backoff
from loader.indexes import INDEXES
from connections import backoff_hdlr
from elasticsearch.client import Elasticsearch as ES_client
from elasticsearch import RequestError, ElasticsearchException, helpers


class ESLoader:
    def __init__(self, es: ES_client, index_name: str = "movies") -> None:
        self.es = es
        self.index_name = index_name

    def drop_index(self):
        self.es.indices.delete(index=self.index_name, ignore=[400, 404])

    def create_index(self) -> bool:

        index_exist: bool = False
        try:
            check_index: bool = self.es.indices.exists(self.index_name)
            if not check_index:
                create_result: dict = self.es.indices.create(
                    index=self.index_name, ignore=400, body=INDEXES[self.index_name]
                )
                if "error" in create_result:
                    raise RequestError
                logging.info(create_result)
            else:
                logging.info("Elasticsearch index %s already exists", self.index_name)
            index_exist = True
        except RequestError:
            logging.error(create_result["error"])
        finally:
            self.created_index = index_exist
            return self.created_index

    @backoff.on_exception(backoff.expo, (ElasticsearchException), on_backoff=backoff_hdlr)
    def bulk_index(self, transformed_data: List[dict], last_state: str) -> None:
        # согласен с замечанием, убрал try..except
        if last_state:
            remove_actions = [
                {
                    "_id": transformed_film["_id"],
                    "_op_type": "delete",
                }
                for transformed_film in transformed_data
            ]
            helpers.bulk(
                self.es,
                actions=remove_actions,
                index=self.index_name,
                raise_on_error=False,
            )

        helpers.bulk(
            self.es,
            actions=transformed_data,
            index=self.index_name,
            refresh=True,
            raise_on_error=True,
        )
