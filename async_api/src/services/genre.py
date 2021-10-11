from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from fastapi import Depends
from db.redis import get_redis
from models.genre import Genre
from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from elasticsearch._async.client import logger
from elasticsearch.exceptions import NotFoundError

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


# TODO пока только заглушка


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all_genres(
        self,
    ) -> List[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # genre = await self._genre_from_cache(genre_uuid)
        # if not genre:
        # Если жанра нет в кеше, то ищем его в Elasticsearch
        genres = await self._get_genres_from_elastic()
        # if not genre:
        # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
        #     return None
        # Сохраняем жанр  в кеш
        # await self._put_genre_to_cache(genre)

        return genres

    # get_by_uuid возвращает объект жанра. Он опционален, так как жанр может отсутствовать в базе
    async def get_by_uuid(self, genre_uuid: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre = await self._genre_from_cache(genre_uuid)
        if not genre:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_elastic(genre_uuid)
            if not genre:
                # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
                return None
            # Сохраняем жанр  в кеш
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, genre_uuid: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get("genres", genre_uuid)
            return Genre(id=doc["_id"], **doc["_source"])
        except NotFoundError as not_found_exception:
            logger.error(not_found_exception)

    async def _get_genres_from_elastic(
        self,
    ) -> List[Genre]:
        try:
            genres_list = []
            search_results = await self.elastic.search(
                index="genres",
                body={"query": {"match_all": {}}},
                filter_path=["hits.hits._id", "hits.hits._source"],
                size=20,
            )
            for res in search_results["hits"]["hits"]:
                genres_list.append(Genre(uuid=res["_id"], name=res["_source"]["name"]))
            return genres_list

        except NotFoundError as not_found_exception:
            logger.error(not_found_exception)

    async def _genre_from_cache(self, genre_uuid: str) -> Optional[Genre]:
        # Пытаемся получить данные о жанре из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(genre_uuid)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные о жанре, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            genre.uuid, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
