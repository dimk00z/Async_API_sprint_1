from http import HTTPStatus
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


# TODO дописать модель, реализовать выгрузку. Пока только заглушка


class Genre(BaseModel):
    id: str
    title: str


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{genre_id}", response_model=Genre)
async def genre_details(film_id: str, film_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(film_id)
    if not genre:

        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="gerne not found")

    return Genre(
        id=genre.id,
        title=genre.title,
    )
