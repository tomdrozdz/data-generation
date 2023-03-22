import inspect
import types
import typing as t
from collections import Counter
from collections.abc import Mapping, Sequence

import attr

from udg.data.generator import Generator
from udg.features.base import Feature, HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule


class ModelDefinitionError(Exception):
    pass


class GeneratorNotFoundError(ModelDefinitionError):
    pass


class MultipleGeneratorsError(ModelDefinitionError):
    pass


class InvalidFeatureError(ModelDefinitionError):
    pass


@attr.frozen
class Block:
    generator: Generator
    requirements: Mapping[str, type[Feature]]


@attr.frozen
class ModelDefinition:
    building_blocks: Mapping[type[Feature], Block]
    household_features: Sequence[type[HouseholdFeature]]
    person_features: Sequence[type[PersonFeature]]

    def __attrs_post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_generators(cls, *generators: Generator) -> t.Self:
        building_blocks: dict[type[Feature], Block] = {}
        household_features: list[type[HouseholdFeature]] = []
        person_features: list[type[PersonFeature]] = []

        for generator in generators:
            signature = inspect.signature(generator.generate)

            requirements = {
                name: parameter.annotation
                for name, parameter in signature.parameters.items()
            }

            for return_cls in _discover_return_types(signature.return_annotation):
                building_blocks[return_cls] = Block(
                    generator=generator,
                    requirements=types.MappingProxyType(requirements),
                )

                if issubclass(return_cls, PersonFeature):
                    person_features.append(return_cls)

                if issubclass(return_cls, HouseholdFeature):
                    household_features.append(return_cls)

        # Consistent order when debugging
        household_features.sort(key=lambda cls: cls.__name__)
        person_features.sort(key=lambda cls: cls.__name__)

        return cls(
            building_blocks=types.MappingProxyType(building_blocks),
            household_features=tuple(household_features),
            person_features=tuple(person_features),
        )

    def validate(self) -> None:
        requirements = {
            (feature, requirement, block.generator.__class__)
            for feature, block in self.building_blocks.items()
            for requirement in block.requirements.values()
        }
        duplicates = (
            *_find_duplicates(self.person_features),
            *_find_duplicates(self.household_features),
        )
        overlapping = set(self.person_features) & set(self.household_features)

        exceptions = [
            *(
                GeneratorNotFoundError(
                    f"Basic feature '{basic_feature.__name__}' is required "
                    "but no generator was provided for it"
                )
                for basic_feature in (Schedule, PersonNumber)
                if basic_feature not in self.building_blocks
            ),
            *(
                GeneratorNotFoundError(
                    f"Feature '{feature.__name__}' requires '{requirement.__name__}', "
                    "but no generator was provided for it "
                    f"(required by '{generator.__name__}')"
                )
                for feature, requirement, generator in requirements
                if requirement not in self.building_blocks
            ),
            *(
                MultipleGeneratorsError(
                    f"Found multiple generators for feature '{feature.__name__}'"
                )
                for feature in duplicates
            ),
            *(
                InvalidFeatureError(
                    f"Feature '{feature.__name__}' is both person and household feature"
                )
                for feature in overlapping
            ),
        ]

        if exceptions:
            raise ExceptionGroup("Model definition validation failed", exceptions)


def _discover_return_types(annotation: type) -> t.Iterator[type]:
    if t.get_origin(annotation) is tuple:
        yield from t.get_args(annotation)
    else:
        yield annotation


def _find_duplicates(features: Sequence[type]) -> t.Iterator[type]:
    counter = Counter(features)
    return (feature for feature, count in counter.items() if count > 1)
