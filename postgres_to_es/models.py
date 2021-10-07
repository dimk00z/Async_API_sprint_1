from dataclasses import dataclass, field
from datetime import datetime
from typing import Set


@dataclass(frozen=True)
class Person:
    id: str
    full_name: str
    role: str


@dataclass
class FilmWork:
    id: str
    title: str
    description: str = None
    rating: float = field(default=0.0)
    type: str = None
    created_at: datetime = None
    updated_at: datetime = None
    actors: Set[Person] = field(default_factory=set)
    directors: Set[Person] = field(default_factory=set)
    writers: Set[Person] = field(default_factory=set)
    genres: Set[str] = field(default_factory=set)
