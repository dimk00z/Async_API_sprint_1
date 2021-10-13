from functools import lru_cache
from typing import Dict, List, Optional

from aioredis import Redis
from fastapi import Depends
from models.film import Film
from db.redis import get_redis
from db.elastic import get_elastic
from services.base import MainService
from elasticsearch import AsyncElasticsearch
from elasticsearch._async.client import logger
from elasticsearch.exceptions import RequestError, NotFoundError

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(MainService):
    index = "movies"
    model = Film

    async def get_films(
        self,
        path: str,
        sort: Optional[str],
        page_number: int,
        page_size: int,
        filter_genre: Optional[str] = "",
        query: str = "",
    ) -> List[Dict]:
        response = await self._get_values_from_cache(
            path,
        )
        if not response:
            return await self._search(
                path=path,
                sort=sort,
                filter_genre=filter_genre,
                page_number=page_number,
                page_size=page_size,
                query=query,
            )

        else:
            return [
                self.model(**dict(doc)["_source"])
                for doc in dict(response)["hits"]["hits"]
            ]

    async def _search(
        self,
        path: str,
        sort: Optional[str],
        page_number: int = 1,
        page_size: int = 20,
        filter_genre: Optional[str] = "",
        query: str = "",
    ) -> List[dict]:
        try:
            imdb_sorting = "desc"
            if sort == "imdb_rating":
                imdb_sorting = "asc"
            first_field = 0 if page_number in (0, 1) else page_number * page_size
            films = []
            body = {"query": {"match_all": {}}}
            if filter_genre:
                body["query"] = {
                    "nested": {
                        "path": "genres",
                        "query": {
                            "bool": {
                                "must": [{"match": {f"genres.uuid": filter_genre}}]
                            }
                        },
                    }
                }

            elif query != "":
                body["query"] = {
                    "match": {"title": query},
                    "match": {"description": query},
                }
            search_results = await self.elastic.search(
                index=self.index,
                body=body,
                filter_path=["hits.hits._id", "hits.hits._source"],
                size=page_size,
                from_=first_field,
                sort=f"imdb_rating:{imdb_sorting},",
            )
            await self._put_to_cache(path, search_results)

            if search_results:
                for res in search_results["hits"]["hits"]:
                    films.append(Film(**res["_source"]))
            return films

        except (NotFoundError, KeyError) as not_found_exception:
            logger.error(not_found_exception)
        except RequestError as request_error:
            print(request_error, dir(request_error))


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
