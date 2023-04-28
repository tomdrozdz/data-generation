from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.household import Region


class RegionSampler(Generator[Region]):
    def __init__(self) -> None:
        data = load_json("wroclaw/unsorted/region.json")
        self._sampler = MultinomialSampler(
            values=list(int(k) for k in data),
            probabilities=list(data.values()),
        )

    def generate(self) -> Region:
        return Region(self._sampler.sample())
