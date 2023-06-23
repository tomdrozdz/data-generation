class Feature:
    pass


class UniqueSubclassesMixin:
    subclasses: dict[str, type] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.__name__ in cls.subclasses:
            existing = cls.subclasses[cls.__name__]

            existing_name = f"{existing.__module__}.{existing.__name__}"
            new_name = f"{cls.__module__}.{cls.__name__}"

            # A bit of a hack to allow creation of `attrs` slots classes:
            # If two classes are defined in the same place, override the existing one.

            if existing_name != new_name:
                raise ValueError(
                    f"Feature with the name '{cls.__name__}' is already defined "
                    f"(raised by '{new_name}' because of '{existing_name}')."
                )

        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__name__] = cls


class PersonFeature(Feature, UniqueSubclassesMixin):
    pass


class FamilyFeature(Feature, UniqueSubclassesMixin):
    pass


class HouseholdFeature(Feature, UniqueSubclassesMixin):
    pass
