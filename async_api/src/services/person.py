import asyncio
import logging
from uuid import UUID
from functools import lru_cache

from fastapi import Depends
from db.elastic import get_elastic
from services.base import MainService
from services.film import FilmService
from elasticsearch import AsyncElasticsearch
from models.person import Person, PersonFilm, PersonRole

PERSON_REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

logger = logging.getLogger(__name__)


class PersonService(MainService):
    model = Person
    index = "persons"

    async def get_by_full_name(
        self, query_full_name: str, page_number: int = 0, page_size: int = 25
    ) -> list[Person]:
        persons = await self._search(
            query={
                "match": {"full_name": {"query": query_full_name, "fuzziness": "auto"}}
            },
            filter_path=["hits.hits._source"],
            from_=page_number * page_size,
            size=page_size,
        )
        return [self.model(**doc["_source"]) for doc in persons]

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

    async def get_films_by_role(
        self, *, person_uuid: UUID, elastic_path: str, role: PersonRole
    ) -> list[PersonFilm]:
        films = await self._search(
            index=FilmService.index,
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
        return [PersonFilm(role=role, **film["_source"]) for film in films]


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
