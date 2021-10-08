from http import HTTPStatus
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.person import PersonService, get_person_service

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


# TODO дописать модель, реализовать выгрузку. Пока только заглушка


class Person(BaseModel):
    id: str
    title: str


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{person_id}", response_model=Person)
async def genre_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:

        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="gerne not found")

    return Person(
        id=person.id,
        title=person.title,
    )
