from uuid import UUID
from typing import Optional
from functools import lru_cache

from aioredis import Redis
from fastapi import Depends
from db.redis import get_redis
from models.person import Person
from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

# TODO пока только заглушка, нету ETL


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_uuid(self, person_uuid: UUID) -> Optional[Person]:
        person = await self._person_from_cache(person_uuid)
        if not person:
            person = await self._get_person_from_elastic(person_uuid)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_uuid: UUID) -> Optional[Person]:
        doc = await self.elastic.get("person", str(person_uuid))
        return Person(uuid=doc["_id"], **doc["_source"])

    async def _person_from_cache(self, person_uuid: UUID) -> Optional[Person]:
        data = await self.redis.get(str(person_uuid))
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            str(person.uuid), person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
