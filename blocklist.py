import importlib.abc
import sys
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import List, Sequence, Union


class BlocklistFinder(importlib.abc.MetaPathFinder):
    def __init__(self, blocked: List[str]):
        self._blocked = blocked

    def find_spec(
        self,
        fullname: str,
        _path: Sequence[Union[bytes, str]] | None,
        _target: ModuleType | None = None,
    ) -> None:
        if fullname in self._blocked:
            raise ImportError(f"Cannot import {fullname!r} it is blocked")
        return None


if __name__ == "__main__":
    sys.meta_path.insert(0, BlocklistFinder(["socket"]))
    import http.server
