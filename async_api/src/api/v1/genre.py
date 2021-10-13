from uuid import UUID
from http import HTTPStatus
from typing import Dict, List, Optional

from models.genre import Genre
from core.utilites import get_path_from_url
from services.genre import GenreService, get_genre_service
from fastapi import Depends, Request, APIRouter, HTTPException

router = APIRouter()

genres = Optional[List[Dict[str, str]]]


@router.get("/")
async def genre_list(
    request: Request,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    return await genre_service.genre_list(get_path_from_url(request))


@router.get("/{genre_uuid}")
async def genre_details(
    request: Request,
    genre_uuid: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Optional[Genre]:
    genre = await genre_service.get_by_uuid(get_path_from_url(request), genre_uuid)
    if genre:
        return genre
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
