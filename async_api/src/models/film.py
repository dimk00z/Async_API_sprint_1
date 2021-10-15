from uuid import UUID

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
    genres: list[Genre] = None
    writers: list[PersonForFilm] = None
    actors: list[PersonForFilm] = None
    directors: list[PersonForFilm] = None
