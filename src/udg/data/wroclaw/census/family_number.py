from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.family import PersonNumber
from udg.features.household import FamilyNumber, HouseholdStructure


class FamilyNumberSampler(Generator[FamilyNumber]):
    def __init__(self) -> None:
        self._person_sampler = ConditionalSampler[PersonNumber](
            data=load_json(
                "wroclaw/census/person_number.json",
                structure=[HouseholdStructure, PersonNumber],
                out=MultinomialSampler,
            )
        )

    def generate(self, household_structure: HouseholdStructure) -> FamilyNumber:
        match household_structure:
            case (
                HouseholdStructure.SINGLE_FAMILY
                | HouseholdStructure.SINGLE_FAMILY_WITH_PARENTS
                | HouseholdStructure.SINGLE_FAMILY_WITH_OTHERS
            ):
                return FamilyNumber(1)
            case (
                HouseholdStructure.TWO_FAMILIES_RELATED
                | HouseholdStructure.TWO_FAMILIES_UNRELATED
            ):
                return FamilyNumber(2)
            case HouseholdStructure.THREE_AND_MORE_FAMILIES:
                return FamilyNumber(3)
            case HouseholdStructure.UNRELATED:
                person_number = int(self._person_sampler.sample(household_structure))
                return FamilyNumber(person_number)
