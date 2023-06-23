import functools
import typing as t

from udg.features.base import FamilyFeature, HouseholdFeature, PersonFeature

from .converter import converter

FeatureType = t.TypeVar("FeatureType", HouseholdFeature, PersonFeature, FamilyFeature)


@functools.cache
def _get_type(name: str) -> type[FeatureType]:
    type_ = (
        HouseholdFeature.subclasses.get(name)
        or FamilyFeature.subclasses.get(name)
        or PersonFeature.subclasses.get(name)
    )

    if type_ is None:
        # TODO: Add an option to pass extra user defined types somewhere,
        # if a type is not imported it won't be in subclasses (although passing it
        # anywhere would require importing it, maybe just pass and discard it...)
        raise ValueError(f"Could not find type '{name}'")

    return t.cast(type[FeatureType], type_)


def deserialize(data: dict[str, t.Any]) -> dict[type[FeatureType], FeatureType]:
    features = {}

    for type_str, value in data.items():
        feature_type = _get_type(type_str)
        features[feature_type] = converter.structure(value, feature_type)

    return features


def serialize(features: dict[type[FeatureType], FeatureType]) -> dict[str, t.Any]:
    return {
        feature_type.__name__: converter.unstructure(value)
        for feature_type, value in features.items()
    }
