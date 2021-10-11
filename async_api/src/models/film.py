from typing import Dict, List, Optional

from .genre import Genre
from .abstract_model import AbstractModel

persons = Optional[List[Dict[str, str]]]
object_names = Optional[List[str]]


class Film(AbstractModel):
    uuid: str
    title: str
    description: str
    imdb_rating: float = None
    genres: List[Genre] = None
    writers: persons = None
    actors: persons = None
    directors: persons = None
