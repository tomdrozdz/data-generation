import typing as t
from concurrent.futures import ThreadPoolExecutor

import attr
from tqdm import tqdm, trange

from udg.features.base import Feature
from udg.features.family import PersonNumber
from udg.features.household import FamilyNumber
from udg.model.definition import ModelDefinition
from udg.model.model import Family, Household, Person, TrafficModel

FeatureToBuild = t.TypeVar("FeatureToBuild", bound=Feature)
Context: t.TypeAlias = dict[
    type[Feature | Household | Family], Feature | Household | Family
]


@attr.define
class Builder:
    model_definition: ModelDefinition

    def _build(
        self,
        cls: type[FeatureToBuild],
        context: Context,
    ) -> FeatureToBuild:
        if (already_generated := context.get(cls)) is not None:
            return t.cast(FeatureToBuild, already_generated)

        block = self.model_definition.building_blocks[cls]

        requirements = {
            name: self._build(requirement_cls, context)
            for name, requirement_cls in block.requirements.items()
        }

        generated_value = block.generator.generate(**requirements)

        if isinstance(generated_value, tuple):
            for value in generated_value:
                context[type(value)] = value

            return t.cast(FeatureToBuild, context[cls])
        else:
            context[cls] = generated_value
            return generated_value

    def _build_person(self, context: Context) -> Person:
        context = context.copy()

        person_features = {
            feature: self._build(feature, context)
            for feature in self.model_definition.person_features
        }

        return Person(features=person_features)

    def _build_family(self, context: Context) -> Family:
        context = context.copy()

        person_number = self._build(PersonNumber, context)
        family_features = {
            feature: self._build(feature, context)
            for feature in self.model_definition.family_features
        }

        persons: list[Person] = []
        family = Family(persons=persons, features=family_features)

        context[Family] = family
        persons.extend(self._build_person(context) for _ in range(person_number))

        return family

    def _build_household(self, *args: t.Any) -> Household:
        context: Context = {}

        family_number = self._build(FamilyNumber, context)
        household_features = {
            feature: self._build(feature, context)
            for feature in self.model_definition.household_features
        }

        families: list[Family] = []
        household = Household(families=families, features=household_features)

        context[Household] = household
        families.extend(self._build_family(context) for _ in range(family_number))

        return household

    def build_model(
        self,
        household_number: int,
        enable_tqdm: bool = False,
    ) -> TrafficModel:
        households = [
            self._build_household()
            for _ in trange(
                household_number,
                disable=not enable_tqdm,
            )
        ]
        return TrafficModel(households=households)

    def _build_until(self, person_number: int, pbar: tqdm) -> list[Household]:
        households: list[Household] = []
        current = 0

        while True:
            household = self._build_household()
            households.append(household)
            persons = sum(len(f.persons) for f in household.families)
            current += persons

            pbar.update(persons)

            if current >= person_number:
                break

        return households

    def _build_until_threaded(
        self,
        executor: ThreadPoolExecutor,
        person_number: int,
        pbar: tqdm,
    ) -> list[Household]:
        households: list[Household] = []
        current = 0

        for household in executor.map(
            self._build_household, (() for _ in range(person_number))
        ):
            households.append(household)
            persons = sum(len(f.persons) for f in household.families)
            current += persons

            pbar.update(persons)

            if current >= person_number:
                break

        executor.shutdown(wait=False, cancel_futures=True)
        return households

    def build_model_until(
        self,
        person_number: int,
        threads: int = 0,
        enable_tqdm: bool = False,
    ) -> TrafficModel:
        with tqdm(total=person_number, disable=not enable_tqdm) as pbar:
            if threads > 0:
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    households = self._build_until_threaded(
                        executor,
                        person_number,
                        pbar,
                    )
            else:
                households = self._build_until(person_number, pbar)

        return TrafficModel(households=households)
