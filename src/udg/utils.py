import inspect
import typing as t
import uuid
from types import ModuleType

import base58

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


def generate_id() -> str:
    return base58.b58encode(uuid.uuid4().bytes).decode()
