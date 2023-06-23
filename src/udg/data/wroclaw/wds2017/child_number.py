from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, MultinomialSampler, load_json
from udg.features.family import ChildNumber, PersonNumber


class ChildNumberSampler(Generator[ChildNumber]):
    def __init__(self) -> None:
        self._sampler = ConditionalSampler[ChildNumber](
            data=load_json(
                "wroclaw/wds2017/child_number.json",
                structure=[PersonNumber, ChildNumber],
                out=MultinomialSampler,
            )
        )

    def generate(self, person_number: PersonNumber) -> ChildNumber:
        return self._sampler.sample(person_number)
