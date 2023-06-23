import typing as t

import attr

from ..base import PersonFeature


@attr.define
class TransportPreferences(PersonFeature):
    pedestrian_inconvenience: int
    bicycle_comfort: int
    public_transport_comfort: int
    public_transport_punctuality: int

    @classmethod
    def for_child(cls) -> t.Self:
        return cls(
            pedestrian_inconvenience=-1,
            bicycle_comfort=-1,
            public_transport_comfort=-1,
            public_transport_punctuality=-1,
        )

    def as_input(self) -> t.Iterator[int]:
        yield self.public_transport_comfort
        yield self.public_transport_punctuality
        yield self.bicycle_comfort
        yield self.pedestrian_inconvenience
