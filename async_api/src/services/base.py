from uuid import UUID
from typing import AnyStr, Callable, Optional

import orjson
import elasticsearch
from aioredis import Redis
from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class MainService:
    # Определяем базовую модель и индекс, будет указываться при добавлении модели жанра
    model = BaseModel
    index = ""

    # Инициализация класса, определение настроек redis и elastic
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):

        self.redis = redis
        self.elastic = elastic

    # Достаем кэш из редиса. В виде ключа используем path от url
    async def _get_from_cache(self, path: str) -> Optional[AnyStr]:
        response = await self.redis.get(path)
        return response

    # Складываем кэш в редис. Ключ - path от url, значение - байтовый массив
    async def _put_to_cache(self, path: str, obj) -> None:
        await self.redis.set(path, orjson.dumps(obj), expire=CACHE_EXPIRE_IN_SECONDS)

    # Получение значений по ключу path
    async def _get_values_from_cache(self, path: str):
        response = await self._get_from_cache(path)
        if response:
            return orjson.loads(response)

        return response

    # Абстрактный вызов метода в Elastic. Можно вызывать любой.
    async def _get_from_elastic(self, es_method: Callable, **kwargs):
        response = await es_method(**kwargs)

        return response

    # Получение значений по uuid
    async def get_by_uuid(self, path: str, uuid: UUID):
        try:
            response = await self._get_values_from_cache(
                path,
            )
            if not response:
                doc_ = await self._get_from_elastic(
                    self.elastic.get, index=self.index, id=str(uuid)
                )
                await self._put_to_cache(path, doc_)
                return self.model(**doc_["_source"])
            else:
                return self.model(**dict(response)["_source"])

        except elasticsearch.NotFoundError:
            return None

    # Поиск в соответствии с body
    async def _search(self, path: str, body: dict):
        try:
            response = await self._get_values_from_cache(
                path,
            )
            if not response:
                response = await self._get_from_elastic(
                    self.elastic.search,
                    index=self.index,
                    body=body,
                    filter_path=["hits.hits._id", "hits.hits" "._source"],
                )
                await self._put_to_cache(path, response)
                return [
                    self.model(**doc["_source"]) for doc in response["hits"]["hits"]
                ]
            else:
                return [
                    self.model(**dict(doc)["_source"])
                    for doc in dict(response)["hits"]["hits"]
                ]
        except elasticsearch.NotFoundError:
            return None
