import inspect
import typing as t
from types import ModuleType

from udg.data.generator import Generator


def _is_generator(obj: object) -> bool:
    return inspect.isclass(obj) and issubclass(obj, Generator) and obj is not Generator


def collect_generators(module: ModuleType) -> t.Iterator[type[Generator]]:
    submodules = (sub for _, sub in inspect.getmembers(module, inspect.ismodule))

    yield from {
        desired_type
        for mod in (module, *submodules)
        for _, desired_type in inspect.getmembers(mod, _is_generator)
    }
