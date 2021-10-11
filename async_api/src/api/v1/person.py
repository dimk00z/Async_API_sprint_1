from enum import Enum
from uuid import UUID
from typing import List
from http import HTTPStatus

from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException
from services.person import PersonService, get_person_service

router = APIRouter()


# TODO пока только заглушка, нету ETL


class PersonRole(str, Enum):
    actor = "actor"
    writer = "writer"
    director = "director"


class Person(BaseModel):
    uuid: UUID
    full_name: str
    role: PersonRole
    film_ids: List[UUID]


@router.get("/{person_uuid}", response_model=Person)
async def genre_details(
    person_uuid: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person_mocked = Person(
        uuid=person_uuid,
        full_name="Mock Mockovich",
        role=PersonRole.actor,
        film_ids=[],
    )
    person = person_mocked  # await person_service.get_by_uuid(person_uuid)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    return Person(
        uuid=person.uuid,
        full_name=person.full_name,
        role=person.role,
        film_ids=person.film_ids,
    )
