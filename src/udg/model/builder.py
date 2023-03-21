import inspect
import typing as t
from collections import Counter

import attr

from udg.data.generator import Generator
from udg.features.base import Feature, HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule
from udg.model.model import Household, Person, TrafficModel

FeatureToBuild = t.TypeVar("FeatureToBuild", bound=Feature)


class BuilderError(Exception):
    pass


class GeneratorNotFoundError(BuilderError):
    pass


class MultipleGeneratorsError(BuilderError):
    pass


class InvalidFeatureError(BuilderError):
    pass


@attr.define
class _Block:
    generator: Generator
    requirements: dict[str, type[Feature]]


class Builder:
    def __init__(self, *generators: Generator) -> None:
        self._building_blocks: dict[type[Feature], _Block] = {}

        self._household_features: list[type[HouseholdFeature]] = []
        self._person_features: list[type[PersonFeature]] = []

        for generator in generators:
            signature = inspect.signature(generator.generate)

            requirements = {
                name: parameter.annotation
                for name, parameter in signature.parameters.items()
            }

            for return_cls in _discover_return_types(signature.return_annotation):
                self._building_blocks[return_cls] = _Block(
                    generator=generator,
                    requirements=requirements,
                )

                if issubclass(return_cls, PersonFeature):
                    self._person_features.append(return_cls)

                if issubclass(return_cls, HouseholdFeature):
                    self._household_features.append(return_cls)

        self._validate_generators()

        # Consistent order when debugging
        self._household_features.sort(key=lambda cls: cls.__name__)
        self._person_features.sort(key=lambda cls: cls.__name__)

    def _validate_generators(self) -> None:
        for basic_feature in (Schedule, PersonNumber):
            if basic_feature not in self._building_blocks:
                raise GeneratorNotFoundError(
                    f"Basic feature '{basic_feature.__name__}' is required "
                    "but no generator was provided for it"
                )

        requirements = {
            (feature, requirement, block.generator.__class__)
            for feature, block in self._building_blocks.items()
            for requirement in block.requirements.values()
        }
        for feature, requirement, generator in requirements:
            if requirement not in self._building_blocks:
                raise GeneratorNotFoundError(
                    f"Feature '{feature.__name__}' requires '{requirement.__name__}' "
                    "but no generator was provided for it "
                    f"(required by '{generator.__name__}')"
                )

        duplicates = (
            *_find_duplicates(self._person_features),
            *_find_duplicates(self._household_features),
        )
        if duplicates:
            errors = ", ".join(f"'{feature.__name__}'" for feature in duplicates)
            raise MultipleGeneratorsError(
                f"Found multiple generators for following features: {errors}"
            )

        overlapping = set(self._person_features) & set(self._household_features)
        if overlapping:
            errors = ", ".join(f"'{feature.__name__}'" for feature in overlapping)
            raise InvalidFeatureError(
                f"Found features that are both person and household features: {errors}"
            )

    def _build(
        self,
        cls: type[FeatureToBuild],
        context: dict[type[Feature], Feature],
    ) -> FeatureToBuild:
        if (already_generated := context.get(cls)) is not None:
            return t.cast(FeatureToBuild, already_generated)

        block = self._building_blocks[cls]

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
            feature: self._build(feature, context) for feature in self._person_features
        }

        return Person(features=person_features)

    def _build_household(self) -> Household:
        context: dict[type[Feature], Feature] = {}

        person_number = self._build(PersonNumber, context)
        household_features = {
            feature: self._build(feature, context)
            for feature in self._household_features
        }

        persons = [self._build_person(context) for _ in range(person_number)]
        return Household(persons=persons, features=household_features)

    def build_model(self, household_number: int) -> TrafficModel:
        households = [self._build_household() for _ in range(household_number)]
        return TrafficModel(households=households)


def _discover_return_types(annotation: type) -> t.Iterator[type]:
    if t.get_origin(annotation) is tuple:
        yield from t.get_args(annotation)
    else:
        yield annotation


def _find_duplicates(features: list[type]) -> t.Iterator[type]:
    counter = Counter(features)
    return (feature for feature, count in counter.items() if count > 1)
