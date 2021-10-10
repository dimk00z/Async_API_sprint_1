from uuid import UUID
from typing import Set
from datetime import date, datetime
from dataclasses import field, dataclass


@dataclass(frozen=True)
class Person:
    uuid: UUID
    full_name: str
    role: str = None
    birth_date: date = None
    updated_at: datetime = None


@dataclass(frozen=True)
class Genre:
    uuid: UUID
    name: str
    updated_at: datetime = None


@dataclass
class FilmWork:
    uuid: UUID
    title: str
    description: str = None
    rating: float = field(default=0.0)
    type: str = None
    created_at: datetime = None
    updated_at: datetime = None
    actors: Set[Person] = field(default_factory=set)
    directors: Set[Person] = field(default_factory=set)
    writers: Set[Person] = field(default_factory=set)
    genres: Set[Genre] = field(default_factory=set)
