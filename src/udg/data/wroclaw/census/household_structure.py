from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.household import HouseholdStructure


class HouseholdStructureSampler(Generator[HouseholdStructure]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/census/household_structure.json",
                structure=[HouseholdStructure],
            )
        )

    def generate(self) -> HouseholdStructure:
        return self._sampler.sample()
