from .base import HouseholdFeature


class CarNumber(HouseholdFeature, int):
    pass


class PersonNumber(HouseholdFeature, int):
    pass
