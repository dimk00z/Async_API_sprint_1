import asyncio
from uuid import UUID
from http import HTTPStatus

from pydantic import BaseModel
from models.person import PersonRole
from fastapi import Depends, APIRouter, HTTPException
from services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilm(BaseModel):
    uuid: UUID
    title: str
    role: PersonRole


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm] = []


@router.get("/search", response_model=list[Person])
async def person_search(
    query: str,
    page_number: int = 0,
    page_size: int = 25,
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Check me: http://localhost:8000/api/v1/person/search?query=george&page_number=0&page_size=5"""
    persons = await person_service.get_by_full_name(
        query_full_name=query, page_number=page_number, page_size=page_size
    )

    films_of_persons = await asyncio.gather(
        *[person_service.get_films_by_person_uuid(person.uuid) for person in persons]
    )
    for person, films in zip(persons, films_of_persons):
        person.films = films

    return [
        Person(uuid=person.uuid, full_name=person.full_name, films=person.films)
        for person in persons
    ]


@router.get("/{person_uuid}/film")
async def person_films(
    person_uuid: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonFilm]:
    """Check me: http://localhost:8000/api/v1/person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/film"""
    person_films = await person_service.get_films_by_person_uuid(person_uuid)

    return [
        PersonFilm(uuid=film.uuid, title=film.title, role=film.role)
        for film in person_films
    ]


@router.get("/{person_uuid}", response_model=Person)
async def person_details(
    person_uuid: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    """Check me: http://localhost:8000/api/v1/person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"""
    person = await person_service.get_by_uuid(person_uuid)
    person_films = await person_service.get_films_by_person_uuid(person_uuid)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    return Person(uuid=person.uuid, full_name=person.full_name, films=person_films)
