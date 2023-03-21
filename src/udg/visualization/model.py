from rich import print
from rich.tree import Tree

from udg.features.base import Feature
from udg.model.builder import Builder
from udg.model.model import Household, Person


class ModelTree:
    def __init__(self, builder: Builder) -> None:
        self._household_features = builder._household_features.copy()
        self._person_features = builder._person_features.copy()
        self._requirements = {
            feature: tuple(block.requirements.values())
            for feature, block in builder._building_blocks.items()
        }

    def _add(self, tree: Tree, feature: type[Feature], fmt: str) -> None:
        branch = tree.add(f"{fmt}{feature.__name__}")
        for requirement in self._requirements[feature]:
            self._add(branch, requirement, fmt)

    def _count(self, feature: type[Feature]) -> int:
        if requirements := self._requirements[feature]:
            return 1 + sum(self._count(requirement) for requirement in requirements)

        return 1

    def build_tree(self) -> Tree:
        model = Tree("[red]Model")
        household_tree = model.add(f"[blue]{Household.__name__}")
        person_tree = model.add(f"[green]{Person.__name__}")

        for household_feature in sorted(self._household_features, key=self._count):
            self._add(household_tree, household_feature, "[turquoise2]")

        for person_feature in sorted(self._person_features, key=self._count):
            self._add(person_tree, person_feature, "[light_green]")

        return model

    def print(self) -> None:
        tree = self.build_tree()
        print(tree)
