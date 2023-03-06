import inspect
import typing as t
from types import ModuleType

from blocks import Generator


def collect_generators(module: ModuleType) -> t.Iterator[type[Generator]]:
    submodules = (sub for _, sub in inspect.getmembers(module, inspect.ismodule))
    is_desired_type = (
        lambda o: inspect.isclass(o) and issubclass(o, Generator) and not o is Generator
    )

    yield from {
        desired_type
        for mod in (module, *submodules)
        for _, desired_type in inspect.getmembers(mod, is_desired_type)
    }
