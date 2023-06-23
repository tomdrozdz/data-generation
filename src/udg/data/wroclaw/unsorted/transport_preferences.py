from udg.data.generator import Generator
from udg.data.utils import AgeRange, ConditionalSampler, MultinomialSampler, load_json
from udg.features.person import Age, Sex, TransportPreferences


class TransportPreferencesSampler(Generator[TransportPreferences]):
    def __init__(self) -> None:
        self._pedestrian_inconvenience = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/pedestrian_inconvenience.json",
                structure=[AgeRange, Sex, int],
                out=MultinomialSampler,
            )
        )

        self._bicycle_comfort = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/bicycle_comfort.json",
                structure=[AgeRange, Sex, int],
                out=MultinomialSampler,
            )
        )

        self._public_transport_comfort = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/public_transport_comfort.json",
                structure=[AgeRange, Sex, int],
                out=MultinomialSampler,
            )
        )

        self._public_transport_punctuality = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/public_transport_punctuality.json",
                structure=[AgeRange, Sex, int],
                out=MultinomialSampler,
            )
        )

    def generate(self, age: Age, sex: Sex) -> TransportPreferences:
        if age <= 5:
            return TransportPreferences.for_child()

        return TransportPreferences(
            pedestrian_inconvenience=self._pedestrian_inconvenience.sample(age, sex),
            bicycle_comfort=self._bicycle_comfort.sample(age, sex),
            public_transport_comfort=self._public_transport_comfort.sample(age, sex),
            public_transport_punctuality=self._public_transport_punctuality.sample(
                age, sex
            ),
        )
