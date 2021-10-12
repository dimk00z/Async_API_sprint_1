from traceback import print_tb
from functools import lru_cache
from typing import Dict, List, Optional

from aioredis import Redis
from fastapi import Depends
from db.redis import get_redis
from db.elastic import get_elastic
from models.film import Film, PersonForFilm
from elasticsearch import AsyncElasticsearch
from elasticsearch._async.client import logger
from elasticsearch.exceptions import NotFoundError

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get("movies", film_id)
            return Film(**doc["_source"])  # uuid=doc["_id"],
        except NotFoundError as not_found_exception:
            logger.error(not_found_exception)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            film.uuid, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_all_films(
        self,
        sort: Optional[str],
        filter_genre: Optional[str],
        page_number: int,
        page_size: int,
    ) -> List[Dict]:

        films = await self._get_films_from_elastic(
            sort=sort,
            filter_genre=filter_genre,
            page_number=page_number,
            page_size=page_size,
        )
        return films

    async def _get_films_from_elastic(
        self,
        sort: Optional[str],
        filter_genre: Optional[str],
        page_number: int,
        page_size: int,
    ) -> List[dict]:
        try:
            imdb_sorting = "desc"
            if sort == "imdb_rating":
                imdb_sorting = "asc"
            first_field = 0 if page_number in (0, 1) else page_number * page_size
            films = []

            body = {"query": {"match_all": {}}}
            if filter_genre:
                body = {
                    "query": {
                        "nested": {
                            "path": "genres",
                            "query": {
                                "bool": {
                                    "must": [{"match": {f"genres.uuid": filter_genre}}]
                                }
                            },
                        }
                    }
                }

            search_results = await self.elastic.search(
                index="movies",
                body=body,
                filter_path=["hits.hits._id", "hits.hits._source"],
                size=page_size,
                from_=first_field,
                sort=f"imdb_rating:{imdb_sorting},",
            )
            for res in search_results["hits"]["hits"]:
                films.append(Film(**res["_source"]))
            return films

        except (NotFoundError, KeyError) as not_found_exception:
            logger.error(not_found_exception)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
