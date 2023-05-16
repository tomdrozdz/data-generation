from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.household import Region


class RegionSampler(Generator[Region]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/unsorted/region.json",
                structure=[Region],
            )
        )

    def generate(self) -> Region:
        return self._sampler.sample()
