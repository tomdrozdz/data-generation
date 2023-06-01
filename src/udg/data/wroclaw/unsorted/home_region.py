from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.household import HomeRegion


class HomeRegionSampler(Generator[HomeRegion]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/unsorted/region.json",
                structure=[HomeRegion],
            )
        )

    def generate(self) -> HomeRegion:
        return self._sampler.sample()
