from .base import PersonFeature


class Age(PersonFeature, int):
    pass


# TODO: Some of these should be enums
class Sex(PersonFeature, str):
    pass


class TransportMode(PersonFeature, str):
    pass


# TODO: And this should probably a list of `Stop` classes with a starting time
class Schedule(PersonFeature, dict):
    pass
