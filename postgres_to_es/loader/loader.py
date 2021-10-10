import logging
from typing import List

import backoff
from connections import backoff_hdlr
from elasticsearch.client import Elasticsearch as ES_client
from elasticsearch import RequestError, ElasticsearchException, helpers


class ESLoader:
    def __init__(self, es: ES_client, indexes) -> None:
        self.es = es
        self.indexes = indexes

    def drop_indexes(self):
        for index_name in self.indexes:
            self.es.indices.delete(index=index_name, ignore=[400, 404])

    def create_index(self, index_name: str) -> bool:

        index_exist: bool = False
        try:
            check_index: bool = self.es.indices.exists(index_name)
            if not check_index:
                create_result: dict = self.es.indices.create(
                    index=index_name, ignore=400, body=self.indexes[index_name]
                )
                if "error" in create_result:
                    raise RequestError
                logging.info(create_result)
            else:
                logging.info("Elasticsearch index %s already exists", index_name)
            index_exist = True
        except RequestError:
            logging.error(create_result["error"])
        finally:
            self.created_index = index_exist
            return self.created_index

    def create_indexes(self):
        for index_name in self.indexes:
            self.create_index(index_name=index_name)

    @backoff.on_exception(backoff.expo, (ElasticsearchException), on_backoff=backoff_hdlr)
    def bulk_index(self, transformed_data: List[dict], index_name: str, last_state: str) -> None:
        if last_state:
            remove_actions = [
                {
                    "_id": transformed_value["_id"],
                    "_op_type": "delete",
                }
                for transformed_value in transformed_data
            ]
            helpers.bulk(
                self.es,
                actions=remove_actions,
                index=index_name,
                raise_on_error=False,
            )

        helpers.bulk(
            self.es,
            actions=transformed_data,
            index=index_name,
            refresh=True,
            raise_on_error=True,
        )
