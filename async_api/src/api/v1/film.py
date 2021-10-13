import logging
from uuid import UUID
from http import HTTPStatus
from typing import Dict, List, Optional

from pydantic import BaseModel
from core.utilites import get_path_from_url
from services.film import FilmService, get_film_service
from fastapi import Query, Depends, Request, APIRouter, HTTPException

from .genre import Genre

router = APIRouter()

persons = Optional[List[Dict[str, str]]]


class PersonForFilm(BaseModel):
    uuid: UUID
    full_name: str


class Film(BaseModel):
    uuid: UUID
    title: str
    description: str = None
    imdb_rating: float = None
    genres: List[Genre] = None
    writers: List[PersonForFilm] = None
    actors: List[PersonForFilm] = None
    directors: List[PersonForFilm] = None


async def get_films(
    path: str,
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[str] = "",
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = 1,
    page_size: int = 50,
    query: Optional[str] = "",
):
    films = await film_service.get_films(
        path=path,
        sort=sort,
        filter_genre=filter_genre if filter_genre is not Query(None) else "",
        page_number=page_number,
        page_size=page_size,
        query=str(query),
    )
    if "error" in films:
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=films["error"])
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


@router.get("/")
async def films_list(
    request: Request,
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[str] = Query(None, alias="filter[genre]"),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]"),
    page_size: int = Query(50, alias="page[size]"),
) -> List[Dict]:
    return await get_films(
        path=get_path_from_url(request),
        film_service=film_service,
        sort=sort,
        filter_genre=filter_genre,
        page_number=page_number,
        page_size=page_size,
    )


@router.get("/search")
async def films_search(
    request: Request,
    film_service: FilmService = Depends(get_film_service),
    sort_: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$", alias="page[size]"),
    page_number_: int = Query(1, alias="page[number]"),
    page_size_: int = Query(50, alias="page[size]"),
    query_: Optional[str] = Query(None, title="Поисковая строка", alias="query"),
) -> List[Dict]:
    return await get_films(
        path=get_path_from_url(request),
        film_service=film_service,
        sort=sort_,
        query=query_,
        page_number=page_number_,
        page_size=page_size_,
    )


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_uuid}", response_model=Film)
async def film_details(
    request: Request,
    film_uuid: str,
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    film = await film_service.get_by_uuid(
        path=get_path_from_url(request), uuid=film_uuid
    )

    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film.parse_obj(film)
