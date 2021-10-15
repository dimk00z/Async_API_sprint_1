from uuid import UUID
from typing import AnyStr, Callable, Optional

import orjson
import elasticsearch
from aiocache import cached
from pydantic import BaseModel
from db.redis import get_redis_cache_config
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class MainService:
    # Определяем базовую модель и индекс, будет указываться при добавлении модели жанра
    model = BaseModel
    index = ""

    # Инициализация класса, определение настроек redis и elastic
    def __init__(self, elastic: AsyncElasticsearch):

        self.elastic = elastic

    # Абстрактный вызов метода в Elastic. Можно вызывать любой.
    async def _get_from_elastic(self, es_method: Callable, **kwargs):
        response = await es_method(**kwargs)
        return response

    @cached(
        ttl=CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(),
    )
    async def get_by_uuid(self, uuid: UUID):
        try:
            doc_ = await self._get_from_elastic(self.elastic.get, index=self.index, id=str(uuid))
            return self.model(**doc_["_source"])

        except (RequestError, NotFoundError):
            return {}

    @cached(
        ttl=CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(),
    )
    async def _search(self, body: dict, page_size: int = 50, first_field: int = 1, sort: str = ""):
        search_options = {
            "index": self.index,
            "body": body,
            "filter_path": ["hits.hits._id", "hits.hits" "._source"],
            "size": page_size,
            "from_": first_field,
        }
        if sort:
            search_options["sort"] = sort
        try:
            response = await self._get_from_elastic(self.elastic.search, **search_options)
            return [self.model(**doc["_source"]) for doc in response["hits"]["hits"]]
        except (RequestError, NotFoundError):
            return []
