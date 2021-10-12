from http import HTTPStatus
from typing import Dict, List, Optional

from pydantic import BaseModel
from services.film import FilmService, get_film_service
from fastapi import Query, Depends, APIRouter, HTTPException

from .genre import Genre

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


class PersonForFilm(BaseModel):
    uuid: str
    full_name: str


class Film(BaseModel):
    uuid: str
    title: str
    description: str = None
    imdb_rating: float = None
    genres: List[Genre] = None
    writers: List[PersonForFilm] = None
    actors: List[PersonForFilm] = None
    directors: List[PersonForFilm] = None


@router.get("/")
async def films_list(
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[str] = Query(None, alias="filter[genre]"),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]"),
    page_size: int = Query(50, alias="page[size]"),
) -> List[Dict]:

    # пример запроса
    # http://localhost:8000/api/v1/film/?sort=-imdb_rating&filter[genre]=%3Ccomedy-uuid%3E&page[size]=10&page[number]=2

    films = await film_service.get_all_films(
        sort=sort,
        filter_genre=filter_genre,
        page_number=page_number,
        page_size=page_size,
    )
    print(sort, filter_genre, page_number, page_size)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="not one film found"
        )
    return [
        {
            "uuid": film.uuid,
            "title": film.title,
            "imdb_rating": film.imdb_rating,
        }
        for film in films
    ]


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_uuid}", response_model=Film)
async def film_details(
    film_uuid: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film.parse_obj(film)
