from enum import Enum

from ..base import HouseholdFeature


class HouseholdStructure(HouseholdFeature, Enum):
    SINGLE_FAMILY = "single_family"
    SINGLE_FAMILY_WITH_PARENTS = "single_family_with_parents"
    SINGLE_FAMILY_WITH_OTHERS = "single_family_with_others"
    TWO_FAMILIES_RELATED = "two_families_related"
    TWO_FAMILIES_UNRELATED = "two_families_unrelated"
    THREE_AND_MORE_FAMILIES = "three_and_more_families"
    UNRELATED = "unrelated"

    def __str__(self) -> str:
        return self.value
