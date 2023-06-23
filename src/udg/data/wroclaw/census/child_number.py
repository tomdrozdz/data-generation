from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.family import ChildNumber, FamilyType


class ChildNumberSampler(Generator[ChildNumber]):
    def __init__(self) -> None:
        self._sampler = ConditionalSampler[ChildNumber](
            data=load_json(
                "wroclaw/census/child_number.json",
                structure=[FamilyType, ChildNumber],
                out=MultinomialSampler,
            )
        )

    def generate(self, family_type: FamilyType) -> ChildNumber:
        match family_type:
            case (
                FamilyType.MARRIED_WITH_CHILDREN
                | FamilyType.PARTNERS_WITH_CHILDREN
                | FamilyType.MOTHER_WITH_CHILDREN
                | FamilyType.FATHER_WITH_CHILDREN
            ):
                return self._sampler.sample(family_type)
            case _:
                return ChildNumber(0)
