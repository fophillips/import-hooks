import importlib.abc
import importlib.machinery
import sys
from types import ModuleType
from typing import Sequence, Union


class TracingFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[Union[bytes, str]] | None,
        target: ModuleType | None = None,
    ):
        print(f"Looking for: {fullname=} {path=}")
        return None


if __name__ == "__main__":
    sys.meta_path.insert(0, TracingFinder())  # insert our finder as the first

    import datetime

    print(datetime.datetime.now())

