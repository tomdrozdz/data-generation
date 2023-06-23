from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.family import FamilyType
from udg.features.household import HouseholdStructure


class FamilyTypeSampler(Generator[FamilyType]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/census/family_type.json",
                structure=[FamilyType],
            )
        )

    def generate(self, household_structure: HouseholdStructure) -> FamilyType:
        if household_structure is HouseholdStructure.UNRELATED:
            return FamilyType.NONE

        return self._sampler.sample()
