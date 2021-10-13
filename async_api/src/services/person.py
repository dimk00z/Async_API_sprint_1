import asyncio
import logging
from uuid import UUID
from typing import Optional
from functools import lru_cache

from aiocache import cached
from fastapi import Depends
from db.elastic import get_elastic
from db.redis import get_redis_cache_config
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.person import Person, PersonFilm, PersonRole

PERSON_ELASTIC_INDEX = "persons"
PERSON_REDIS_NAMESPACE = "persons"
PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

logger = logging.getLogger(__name__)


class PersonService:
    """В этом сервисе реализовано кеширование через декораторы `aiocache`."""

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @cached(
        ttl=PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(namespace=PERSON_REDIS_NAMESPACE),
    )
    async def get_by_uuid(self, person_uuid: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(
                index="persons", id=str(person_uuid), filter_path="_source"
            )
            return Person(**doc["_source"])
        except NotFoundError:
            logger.error("<Person %s> not found in elastic!", person_uuid)

    @cached(
        ttl=PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(namespace=PERSON_REDIS_NAMESPACE),
    )
    async def get_by_full_name(
        self, query_full_name: str, page_number: int = 0, page_size: int = 25
    ) -> list[Person]:
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

    @cached(
        ttl=PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(namespace=PERSON_REDIS_NAMESPACE),
    )
    async def get_films_by_person_uuid(self, person_uuid: UUID) -> list[PersonFilm]:
        films_as_actor, films_as_writer, films_as_director = await asyncio.gather(
            self.get_films_by_role(
                person_uuid=person_uuid, elastic_path="actors", role=PersonRole.actor
            ),
            self.get_films_by_role(
                person_uuid=person_uuid, elastic_path="writers", role=PersonRole.writer
            ),
            self.get_films_by_role(
                person_uuid=person_uuid,
                elastic_path="directors",
                role=PersonRole.director,
            ),
        )
        films = films_as_actor + films_as_writer + films_as_director
        return films

    @cached(
        ttl=PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS,
        noself=True,
        **get_redis_cache_config(namespace=PERSON_REDIS_NAMESPACE),
    )
    async def get_films_by_role(
        self, *, person_uuid: UUID, elastic_path: str, role: PersonRole
    ) -> list[PersonFilm]:
        films = await self.elastic.search(
            index="movies",
            query={
                "nested": {
                    "path": elastic_path,
                    "query": {
                        "bool": {
                            "must": [{"match": {f"{elastic_path}.uuid": person_uuid}}]
                        }
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
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
