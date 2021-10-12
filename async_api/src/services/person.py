import asyncio
import logging
from uuid import UUID
from typing import Optional
from functools import lru_cache

from aioredis import Redis
from fastapi import Depends
from models.film import Film
from db.redis import get_redis
from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.person import Person, PersonFilm, PersonRole

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
PERSON_CACHE_KEY_PATTERN = "person:{}"

logger = logging.getLogger(__name__)


# TODO: Redis caching


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_uuid(self, person_uuid: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(
                index="persons", id=str(person_uuid), filter_path="_source"
            )
            return Person(**doc["_source"])
        except NotFoundError:
            logger.error("<Person %s> not found in elastic!", person_uuid)

    async def get_by_full_name(
        self, query_full_name: str, page_number: int = 0, page_size: int = 25
    ) -> list[Person]:
        # TODO: checks, validation of parameters
        persons = await self.elastic.search(
            index="persons",
            query={
                "match": {"full_name": {"query": query_full_name, "fuzziness": "auto"}}
            },
            filter_path=["hits.hits._source"],
            from_=page_number * page_size,
            size=page_size,
        )
        persons_hits = [] if not persons else persons["hits"]["hits"]
        return [Person(**doc["_source"]) for doc in persons_hits]

    async def get_films_by_person_uuid(self, person_uuid: UUID) -> list[PersonFilm]:
        # TODO: caching!

        films_as_actor, films_as_writer, films_as_director = await asyncio.gather(
            self.get_films_by_role(
                person_uuid=person_uuid, path="actors", role=PersonRole.actor
            ),
            self.get_films_by_role(
                person_uuid=person_uuid, path="writers", role=PersonRole.writer
            ),
            self.get_films_by_role(
                person_uuid=person_uuid, path="directors", role=PersonRole.director
            ),
        )
        films = films_as_actor + films_as_writer + films_as_director
        return films

    async def get_films_by_role(
        self, *, person_uuid: UUID, path: str, role: PersonRole
    ) -> list[PersonFilm]:
        films = await self.elastic.search(
            index="movies",
            query={
                "nested": {
                    "path": path,
                    "query": {
                        "bool": {"must": [{"match": {f"{path}.uuid": person_uuid}}]}
                    },
                }
            },
            fields=["hits.hits._source.uuid", "hits.hits._source.title"],
        )
        if not films:
            return []
        films = [
            PersonFilm(role=role, **film["_source"]) for film in films["hits"]["hits"]
        ]
        return films


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)


# {
#     "query": {
#         "bool": {
#             "should": [
#             {
#                 "nested": {
#                     "path": "actors",
#                     "query": {
#                         "bool": {
#                         "must": [
#                                 { "match": { "actors.uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a" } }
#                         ]
#                         }
#                     }
#                 }
#             },
#             {
#                 "nested": {
#                     "path": "directors",
#                     "query": {
#                         "bool": {
#                         "must": [
#                                 { "match": { "directors.uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a" } }
#                         ]
#                         }
#                     }
#                 }
#             },
#             {
#                 "nested": {
#                     "path": "writers",
#                     "query": {
#                         "bool": {
#                         "must": [
#                                 { "match": { "writers.uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a" } }
#                         ]
#                         }
#                     }
#                 }
#             }
#         ]
#         }
#     }
# }
