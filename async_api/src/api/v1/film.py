from http import HTTPStatus
from typing import Dict, List, Optional

from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException
from services.film import FilmService, get_film_service

from .genre import Genre

router = APIRouter()

persons = Optional[List[Dict[str, str]]]

class PersonForFilm(BaseModel):
    uuid: str
    full_name:str
class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float = None
    genres: List[Genre] = None
    writers: List[PersonForFilm] = None
    actors: List[PersonForFilm] = None
    directors: List[PersonForFilm] = None


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return Film(
        id=film.uuid,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genres=film.genres,
        writers=film.writers,
        actors=film.actors,
        directors=film.directors,
    )
