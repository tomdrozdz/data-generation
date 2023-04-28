import datetime as dt

import cattrs


def _unstructure_time(value: dt.time) -> str:
    return value.isoformat()


def _structure_time(value: str, type_: type[dt.time]) -> dt.time:
    return type_.fromisoformat(value)


def _unstructure_timedelta(value: dt.timedelta) -> float:
    return value.total_seconds()


def _structure_timedelta(value: float, type_: type[dt.timedelta]) -> dt.timedelta:
    return type_(seconds=value)


def _create_converter() -> cattrs.Converter:
    converter = cattrs.Converter()

    converter.register_unstructure_hook(dt.time, _unstructure_time)
    converter.register_structure_hook(dt.time, _structure_time)

    converter.register_unstructure_hook(dt.timedelta, _unstructure_timedelta)
    converter.register_structure_hook(dt.timedelta, _structure_timedelta)

    return converter


converter = _create_converter()
