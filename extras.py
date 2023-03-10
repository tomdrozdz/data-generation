import typing as t

from feature import Feature
from generator import Generator
from household import CarNumber


class Wealth(Feature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    REQUIRES = [CarNumber]

    def generate(self, requirements: dict[type[Feature], t.Any]) -> Wealth:
        car_number = requirements[CarNumber]

        if car_number <= 1:
            wealth = "poor"
        else:
            wealth = "rich"

        return Wealth(wealth)
