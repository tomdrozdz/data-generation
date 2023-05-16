from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.household import ChildrenNumber, PersonNumber


class ChildrenNumberSampler(Generator[ChildrenNumber]):
    def __init__(self) -> None:
        self._sampler = ConditionalSampler[ChildrenNumber](
            data=load_json(
                "wroclaw/wds2017/children_number.json",
                structure=[PersonNumber, ChildrenNumber],
                out=MultinomialSampler,
            )
        )

    def generate(self, person_number: PersonNumber) -> ChildrenNumber:
        return self._sampler.sample(person_number)
