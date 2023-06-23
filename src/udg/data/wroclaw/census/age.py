import typing as t

from udg.data.generator import Generator
from udg.data.utils import ConditionalSampler, DynamicMultinomialSampler, load_json
from udg.features.family import ChildNumber, FamilyType
from udg.features.household import HouseholdStructure
from udg.features.person import Age, Role, Sex
from udg.model.model import Family, Person


def _age(person: Person) -> Age:
    return person.features[Age]  # type: ignore[return-value]


def _iter_role(family: Family, role: Role) -> t.Iterator[Person]:
    return (person for person in family.persons if person.features[Role] is role)


class AgeSampler(Generator[Age]):
    def __init__(self) -> None:
        data = load_json(
            "wroclaw/census/age.json",
            structure=[Sex],
        )

        for dist in data.values():
            oldest = dist.pop("90+")
            smoothed = oldest / 10
            for i in range(90, 100):
                dist[str(i)] = smoothed

        self._sampler = ConditionalSampler[Age](
            {
                sex: DynamicMultinomialSampler.from_dict(
                    {Age(age): prob for age, prob in dist.items()}
                )
                for sex, dist in data.items()
            }
        )

    def generate(
        self,
        household_structure: HouseholdStructure,
        family: Family,
        family_type: FamilyType,
        child_number: ChildNumber,
        role: Role,
        sex: Sex,
    ) -> Age:
        if role is Role.CHILD:
            return self._sampler.sample(sex, to=24)
        elif role is Role.MOTHER:
            if child_number > 0:
                youngest_child_age = _age(min(_iter_role(family, Role.CHILD), key=_age))
                oldest_child_age = _age(max(_iter_role(family, Role.CHILD), key=_age))
                return self._sampler.sample(
                    sex,
                    from_=oldest_child_age + 18,
                    to=youngest_child_age + 50,
                )
        elif role is Role.FATHER:
            if family_type is FamilyType.FATHER_WITH_CHILDREN:
                oldest_child_age = _age(max(_iter_role(family, Role.CHILD), key=_age))
                youngest_child_age = _age(min(_iter_role(family, Role.CHILD), key=_age))
                return self._sampler.sample(
                    sex,
                    from_=oldest_child_age + 18,
                    to=youngest_child_age + 60,
                )
            else:
                mother_age = _age(next(_iter_role(family, Role.MOTHER)))
                sampler: DynamicMultinomialSampler[Age] = self._sampler.sampler_for(sex)  # type: ignore[assignment]
                return sampler.sample_normal(mu=mother_age + 3, sigma=10, from_=18)
        else:
            if household_structure is HouseholdStructure.SINGLE_FAMILY_WITH_PARENTS:
                mother = next(_iter_role(family, Role.MOTHER), None)
                father = next(_iter_role(family, Role.FATHER), None)

                mother_age = _age(mother) if mother is not None else Age(99)
                father_age = _age(father) if father is not None else Age(99)

                sampler = self._sampler.sampler_for(sex)  # type: ignore[assignment]
                return sampler.sample_normal(
                    mu=min(mother_age, father_age) + 24,
                    sigma=6,
                )

        return self._sampler.sample(sex, from_=24)
