from http import HTTPStatus
from typing import Dict, List, Optional

from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException
from services.film import FilmService, get_film_service

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float = None
    genres: Optional[List[str]] = None
    writers: persons = None
    actors: persons = None
    directors: persons = None


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(
        id=film.id,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genres=film.genres,
        writers=film.writers,
        actors=film.actors,
        directors=film.directors,
    )
