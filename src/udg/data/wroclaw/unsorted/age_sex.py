import random

from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.person import Age, Sex


class AgeSexSampler(Generator[tuple[Age, Sex]]):
    def __init__(self) -> None:
        data = load_json("wroclaw/unsorted/age_sex.json")

        missing = data.pop("0-5") / 2
        data["0-5_K"], data["0-5_M"] = missing, missing

        # TODO: I think this should be already done in the JSON
        keys = [
            k.replace("_", "-").replace("x", "99").replace("K", "F").split("-")
            for k in data
        ]

        self._sampler = MultinomialSampler(
            values=[
                (int(age_from), int(age_to), Sex(sex)) for age_from, age_to, sex in keys
            ],
            probabilities=list(data.values()),
        )

    def generate(self) -> tuple[Age, Sex]:
        age_from, age_to, sex = self._sampler.sample()
        return Age(random.randint(age_from, age_to)), Sex(sex)
