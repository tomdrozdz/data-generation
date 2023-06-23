from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.family import CarNumber, ChildNumber, FamilyType


class CarNumberSampler(Generator[CarNumber]):
    def __init__(self) -> None:
        self._sampler = ConditionalSampler[CarNumber](
            data=load_json(
                "wroclaw/wds2017/car_number.json",
                structure=[FamilyType, ChildNumber, CarNumber],
                out=MultinomialSampler,
            )
        )

    def generate(self, family_type: FamilyType, child_number: ChildNumber) -> CarNumber:
        return self._sampler.sample(family_type, child_number)
