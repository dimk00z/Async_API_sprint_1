from enum import Enum
from uuid import UUID

from .abstract_model import AbstractModel


class PersonRole(str, Enum):
    actor = "actor"
    writer = "writer"
    director = "director"


class PersonFilm(AbstractModel):
    uuid: UUID
    title: str
    role: PersonRole


class Person(AbstractModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm] = []
