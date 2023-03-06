from feature import Feature


class Age(Feature, int):
    pass


# TODO: Some of these should be enums
class Sex(Feature, str):
    pass


class TransportMode(Feature, str):
    pass


# TODO: And this should probably a list of `Stop` classes with a starting time
class Schedule(Feature, dict):
    pass
