from typing import Optional
from functools import lru_cache

from fastapi import Depends
from models.film import Film
from db.elastic import get_elastic
from services.base import MainService
from elasticsearch import AsyncElasticsearch

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(MainService):
    index = "movies"
    model = Film

    async def get_films(
        self,
        sort: Optional[str],
        page_number: int,
        page_size: int,
        filter_genre: Optional[str] = "",
        query: str = "",
    ) -> list[dict]:
        body = {}
        body["query"] = {"match_all": {}}
        imdb_sorting = "desc"
        if sort == "imdb_rating":
            imdb_sorting = "asc"
        if filter_genre:
            body["query"] = {
                "nested": {
                    "path": "genres",
                    "query": {
                        "bool": {"must": [{"match": {f"genres.uuid": filter_genre}}]}
                    },
                }
            }
        elif query != "":
            body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description"],
                    "type": "best_fields",
                }
            }

        sort = f"imdb_rating:{imdb_sorting},"
        return await self._search(
            body=body,
            sort=sort,
            first_field=page_number * page_size if page_number > 1 else 1,
            page_size=page_size,
        )


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
