from typing import List

from .abstract_model import AbstractModel


class Person(AbstractModel):
    uuid: str
    full_name: str
    role: str
    film_ids: List[str]
