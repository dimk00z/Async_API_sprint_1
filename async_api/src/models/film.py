from typing import Dict, List, Optional, Union

from .abstract_model import AbstractModel

id = Union[str, str]
name = Union[str, str]
persons = Optional[List[Dict[id, name]]]
object_names = Optional[List[str]]


class Film(AbstractModel):
    title: str
    description: str
    imdb_rating: float = None
    genres: object_names = None
    writers: persons = None
    actors: persons = None
    directors: persons = None
    actors_names: object_names = None
    writers_names: object_names = None
