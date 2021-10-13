from functools import lru_cache

from aioredis import Redis
from fastapi import Depends
from db.redis import get_redis
from models.genre import Genre
from db.elastic import get_elastic
from services.base import MainService
from elasticsearch import AsyncElasticsearch


class GenreService(MainService):
    index = "genres"
    model = Genre

    async def genre_list(self, path: str) -> list[Genre]:
        return await self._search(path, {"query": {"match_all": {}}})


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
