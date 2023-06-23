from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_json
from udg.features.person import Role, Sex


class SexSampler(Generator[Sex]):
    def __init__(self) -> None:
        self._sampler = MultinomialSampler.from_dict(
            data=load_json("wroclaw/census/sex.json", structure=[Sex])
        )

    def generate(self, role: Role) -> Sex:
        match role:
            case Role.MOTHER:
                return Sex.F
            case Role.FATHER:
                return Sex.M
            case _:
                return self._sampler.sample()
