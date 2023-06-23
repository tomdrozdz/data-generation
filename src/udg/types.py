import datetime as dt
from enum import Enum

import attr


class Time(dt.time):
    def __add__(self, other: dt.timedelta) -> "Time":
        datetime = dt.datetime.combine(dt.date(2, 2, 2), self) + other
        return Time(
            datetime.hour,
            datetime.minute,
            datetime.second,
            datetime.microsecond,
            fold=datetime.fold,
        )


class Region(int):
    pass


@attr.define
class Place:
    id: str
    region: Region
    x: float
    y: float


class TransportMode(Enum):
    CAR = "car"
    PUBLIC_TRANSPORT = "public_transport"
    PEDESTRIAN = "pedestrian"
    BIKE = "bike"
