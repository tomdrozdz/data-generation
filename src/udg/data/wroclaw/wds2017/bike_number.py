from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.family import BikeNumber, ChildNumber, FamilyType


class BikeNumberSampler(Generator[BikeNumber]):
    def __init__(self) -> None:
        self._sampler = ConditionalSampler[BikeNumber](
            data=load_json(
                "wroclaw/wds2017/bike_number.json",
                structure=[FamilyType, ChildNumber, BikeNumber],
                out=MultinomialSampler,
            )
        )

    def generate(
        self,
        family_type: FamilyType,
        child_number: ChildNumber,
    ) -> BikeNumber:
        return self._sampler.sample(family_type, child_number)
