from udg.data.generator import Generator
from udg.features.family import ChildNumber, FamilyType, PersonNumber
from udg.features.household import HouseholdStructure


class PersonNumberSampler(Generator[PersonNumber]):
    def __init__(self) -> None:
        self._single_adult_family_type = {
            FamilyType.MOTHER_WITH_CHILDREN,
            FamilyType.FATHER_WITH_CHILDREN,
        }

        self._household_with_additional_adults = {
            HouseholdStructure.SINGLE_FAMILY_WITH_PARENTS,
            HouseholdStructure.SINGLE_FAMILY_WITH_OTHERS,
        }

    def generate(
        self,
        household_structure: HouseholdStructure,
        family_type: FamilyType,
        child_number: ChildNumber,
    ) -> PersonNumber:
        if family_type is FamilyType.NONE:
            return PersonNumber(1)
        elif family_type in self._single_adult_family_type:
            adult_number = 1
        else:
            adult_number = 2

        if household_structure in self._household_with_additional_adults:
            adult_number += 1

        return PersonNumber(adult_number + child_number)
