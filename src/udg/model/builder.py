import typing as t

import attr

from udg.features.base import Feature
from udg.features.household import PersonNumber
from udg.model.definition import ModelDefinition
from udg.model.model import Household, Person, TrafficModel

FeatureToBuild = t.TypeVar("FeatureToBuild", bound=Feature)


@attr.define
class Builder:
    model_definition: ModelDefinition

    def _build(
        self,
        cls: type[FeatureToBuild],
        context: dict[type[Feature], Feature],
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

    def _build_person(self, context: dict[type[Feature], Feature]) -> Person:
        context = context.copy()

        person_features = {
            feature: self._build(feature, context)
            for feature in self.model_definition.person_features
        }

        return Person(features=person_features)

    def _build_household(self) -> Household:
        context: dict[type[Feature], Feature] = {}

        person_number = self._build(PersonNumber, context)
        household_features = {
            feature: self._build(feature, context)
            for feature in self.model_definition.household_features
        }

        persons = [self._build_person(context) for _ in range(person_number)]
        return Household(persons=persons, features=household_features)

    def build_model(self, household_number: int) -> TrafficModel:
        households = [self._build_household() for _ in range(household_number)]
        return TrafficModel(households=households)
