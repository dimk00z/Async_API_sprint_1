from http import HTTPStatus
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


# TODO дописать модель, реализовать выгрузку. Пока только заглушка


class Genre(BaseModel):
    uuid: UUID
    name: str


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{genre_uuid}", response_model=Genre)
async def genre_details(
        genre_uuid: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_uuid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(
        uuid=genre.uuid,
        name=genre.name,
    )
