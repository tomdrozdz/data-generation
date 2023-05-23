from enum import Enum

from ..base import PersonFeature


class Sex(PersonFeature, Enum):
    M = "M"
    F = "F"

    def __str__(self) -> str:
        return self.value
