from http import HTTPStatus
from typing import Optional

from models.film import Film
from services.film import FilmService, get_film_service
from fastapi import Query, Depends, APIRouter, HTTPException

router = APIRouter()

persons = Optional[list[dict[str, str]]]


async def get_films(
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[str] = "",
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = 1,
    page_size: int = 50,
    query: Optional[str] = "",
):
    films = await film_service.get_films(
        sort=sort,
        filter_genre=filter_genre if filter_genre is not Query(None) else "",
        page_number=page_number,
        page_size=page_size,
        query=str(query),
    )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="not one film found"
        )
    if "error" in films:
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=films["error"])
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
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[str] = Query(None, alias="filter[genre]"),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]"),
    page_size: int = Query(50, alias="page[size]"),
) -> list[dict]:
    return await get_films(
        film_service=film_service,
        sort=sort,
        filter_genre=filter_genre,
        page_number=page_number,
        page_size=page_size,
    )


@router.get("/search")
async def films_search(
    film_service: FilmService = Depends(get_film_service),
    sort_: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$", alias="page[size]"),
    page_number_: int = Query(1, alias="page[number]"),
    page_size_: int = Query(50, alias="page[size]"),
    query_: Optional[str] = Query(None, title="Поисковая строка", alias="query"),
) -> list[dict]:
    return await get_films(
        film_service=film_service,
        sort=sort_,
        query=query_,
        page_number=page_number_,
        page_size=page_size_,
    )


@router.get("/{film_uuid}", response_model=Film)
async def film_details(
    film_uuid: str,
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    film = await film_service.get_by_uuid(uuid=film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film.parse_obj(film)
