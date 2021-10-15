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
    ):
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
        searched_films = await self._search(
            body=body,
            sort=sort,
            filter_path=["hits.hits._id", "hits.hits" "._source"],
            from_=page_number * page_size if page_number > 1 else 0,
            size=page_size,
        )
        return [self.model(**doc["_source"]) for doc in searched_films]


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
