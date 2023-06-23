from collections.abc import Mapping, Sequence
from functools import partial

from rich import print
from rich.tree import Tree

from udg.features.base import Feature
from udg.model.definition import ModelDefinition
from udg.model.model import Family, Household, Person


class AsciiFeatureTree:
    def __init__(self, model_definition: ModelDefinition) -> None:
        self._model_definition = model_definition

    def _add(
        self,
        tree: Tree,
        feature: type[Feature],
        requirements: Mapping[type[Feature], Sequence[type[Feature]]],
        fmt: str,
    ) -> None:
        branch = tree.add(f"{fmt}{feature.__name__}")
        for requirement in requirements[feature]:
            self._add(branch, requirement, requirements, fmt)

    def _count(
        self,
        feature: type[Feature],
        requirements: Mapping[type[Feature], Sequence[type[Feature]]],
    ) -> int:
        if feature_requirements := requirements[feature]:
            return 1 + sum(
                self._count(requirement, requirements)
                for requirement in feature_requirements
            )

        return 1

    def build_tree(self) -> Tree:
        household_features = self._model_definition.household_features
        family_features = self._model_definition.family_features
        person_features = self._model_definition.person_features
        requirements = {
            feature: tuple(
                v for v in block.requirements.values() if v not in {Family, Household}
            )
            for feature, block in self._model_definition.building_blocks.items()
        }
        count_requirements = partial(self._count, requirements=requirements)

        model = Tree("[red]Model")
        household_tree = model.add(f"[blue]{Household.__name__}")
        family_tree = model.add(f"[yellow]{Family.__name__}")
        person_tree = model.add(f"[green]{Person.__name__}")

        for household_feature in sorted(household_features, key=count_requirements):
            self._add(household_tree, household_feature, requirements, "[turquoise2]")

        for family_feature in sorted(family_features, key=count_requirements):
            self._add(family_tree, family_feature, requirements, "[yellow1]")

        for person_feature in sorted(person_features, key=count_requirements):
            self._add(person_tree, person_feature, requirements, "[light_green]")

        return model

    def print(self) -> None:
        tree = self.build_tree()
        print(tree)
