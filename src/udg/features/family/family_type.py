from enum import Enum

from ..base import FamilyFeature


class FamilyType(FamilyFeature, Enum):
    MARRIED = "married"
    MARRIED_WITH_CHILDREN = "married_with_children"
    PARTNERS = "partners"
    PARTNERS_WITH_CHILDREN = "partners_with_children"
    MOTHER_WITH_CHILDREN = "mother_with_children"
    FATHER_WITH_CHILDREN = "father_with_children"
    NONE = "none"

    def __str__(self) -> str:
        return self.value
