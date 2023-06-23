from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.family import PersonNumber


class PersonNumberSampler(Generator[PersonNumber]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/wds2017/person_number.json",
                structure=[PersonNumber],
            )
        )

    def generate(self) -> PersonNumber:
        return self._sampler.sample()
