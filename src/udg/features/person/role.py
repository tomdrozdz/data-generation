from enum import Enum

from ..base import PersonFeature


class Role(PersonFeature, Enum):
    MOTHER = "mother"
    FATHER = "father"
    CHILD = "child"
    OTHER = "other"

    def __str__(self) -> str:
        return self.value
