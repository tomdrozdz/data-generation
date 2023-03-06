import inspect
import typing as t

from blocks import Generator
from feature import Feature
from household import PersonNumber
from model import Household, Person, TrafficModel
from person import Schedule

ThingToBuild = t.TypeVar("ThingToBuild", bound=Feature)


class Builder:
    def __init__(
        self,
        *generators: type[Generator],
        person_extras: list[type[Feature]] | None = None,
        household_extras: list[type[Feature]] | None = None,
    ) -> None:
        self.person_extras = person_extras or []
        self.household_extras = household_extras or []

        self.generator_for: dict[type[Feature], Generator] = {}

        for generator_cls in generators:
            signature = inspect.signature(generator_cls.generate)
            return_cls = signature.return_annotation

            # TODO: Define some class method that allows generators to load their data
            # (or just use injector package for this part)
            generator = generator_cls()

            self.generator_for[return_cls] = generator

    def _build(self, cls: type[ThingToBuild], context: dict) -> ThingToBuild:
        if (already_generated := context.get(cls)) is not None:
            return already_generated

        try:
            generator = self.generator_for[cls]
        except KeyError:
            raise Exception(f"No generator provided for class '{cls.__name__}'")

        requirements_classes = generator.REQUIRES

        requirements = {
            requirement_cls: self._build(requirement_cls, context)
            for requirement_cls in requirements_classes
        }

        generated_value = generator.generate(requirements)
        context[cls] = generated_value
        return generated_value

    def _build_person(self, context: dict) -> Person:
        context = context.copy()

        person_features = {
            feature: self._build(feature, context) for feature in Person.BASIC_FEATURES
        }

        schedule = self._build(Schedule, context)

        extras = {
            feature: self._build(feature, context) for feature in self.person_extras
        }

        return Person(
            schedule=schedule,
            features=person_features,
            user_defined_extras=extras,
        )

    def _build_household(self) -> Household:
        context: dict = {}

        person_number = self._build(PersonNumber, context)
        household_features = {
            feature: self._build(feature, context)
            for feature in Household.BASIC_FEATURES
        }
        extras = {
            feature: self._build(feature, context) for feature in self.household_extras
        }

        persons = [self._build_person(context) for _ in range(person_number)]

        return Household(
            person_number=person_number,
            persons=persons,
            features=household_features,
            user_defined_extras=extras,
        )

    def build_model(self, household_number: int) -> TrafficModel:
        households = [self._build_household() for _ in range(household_number)]
        return TrafficModel(households)
