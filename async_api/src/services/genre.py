from functools import lru_cache

from fastapi import Depends
from models.genre import Genre
from db.elastic import get_elastic
from services.base import MainService
from elasticsearch import AsyncElasticsearch


class GenreService(MainService):
    index = "genres"
    model = Genre

    async def genre_list(self) -> list[Genre]:
        return await self._search({"query": {"match_all": {}}})


@lru_cache()
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
