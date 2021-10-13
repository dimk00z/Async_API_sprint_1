from uuid import UUID
from typing import List

from pydantic import BaseModel

from .genre import Genre
from .abstract_model import AbstractModel


class PersonForFilm(BaseModel):
    uuid: UUID
    full_name: str


class Film(AbstractModel):
    uuid: UUID
    title: str
    description: str = None
    imdb_rating: float = None
    genres: List[Genre] = None
    writers: List[PersonForFilm] = None
    actors: List[PersonForFilm] = None
    directors: List[PersonForFilm] = None
