import random

from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.person import Age, Sex


class AgeSexSampler(Generator[tuple[Age, Sex]]):
    def __init__(self) -> None:
        data = load_json("wroclaw/unsorted/age_sex.json", out=dict)

        missing = data.pop("0-5") / 2
        data["0-5_F"], data["0-5_M"] = missing, missing

        keys = [k.replace("_", "-").split("-") for k in data]

        self._sampler = MultinomialSampler.from_dict(
            {
                (int(age_from), int(age_to), Sex(sex)): prob
                for (age_from, age_to, sex), prob in zip(keys, data.values())
            }
        )

    def generate(self) -> tuple[Age, Sex]:
        age_from, age_to, sex = self._sampler.sample()
        return Age(random.randint(age_from, age_to)), sex
