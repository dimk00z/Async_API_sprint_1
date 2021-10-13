from uuid import UUID

from .abstract_model import AbstractModel


class Genre(AbstractModel):
    uuid: UUID
    name: str
