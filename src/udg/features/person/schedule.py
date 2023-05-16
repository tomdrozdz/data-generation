import datetime as dt

import attr

from ..base import PersonFeature

# TODO: Is `start_time` a property of `Schedule`? Does every `Stop` has a `start_time`?
# The previous model had it basically as a `Schedule` property I think...


@attr.define
class Stop:
    start_time: dt.time
    place: str


@attr.define
class SetLengthStop(Stop):
    duration: dt.timedelta


@attr.define
class SetEndStop(Stop):
    end_time: dt.time


@attr.define
class Schedule(PersonFeature):
    stops: list[SetLengthStop | SetEndStop]
