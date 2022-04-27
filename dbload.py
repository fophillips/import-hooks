import importlib.abc
import importlib.machinery
import importlib.util
import sqlite3
import sys
import types
from sqlite3.dbapi2 import Connection
from typing import Sequence, Union


class DbLoader(importlib.abc.Loader):
    def __init__(self, package_name: str, dbhandle: Connection):
        self._package_name = package_name
        self._dbhandle = dbhandle

    def provides(self, fullname: str) -> bool:
        if fullname == self._package_name:
            return True
        if not fullname.startswith(self._package_name):
            return False
        cursor = self._dbhandle.cursor()
        cursor.execute("SELECT 1 FROM code WHERE name=?", [fullname])
        row = cursor.fetchone()
        return row is not None

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> types.ModuleType:
        module = types.ModuleType(spec.name)
        if spec.name == self._package_name:
            module.__path__ = []
        return module

    def exec_module(self, module: types.ModuleType) -> None:
        if module.__name__ == self._package_name:
            return
        cursor = self._dbhandle.cursor()
        cursor.execute("SELECT code FROM code WHERE name=?", [module.__name__])
        row = cursor.fetchone()
        exec(row[0], module.__dict__)


class DbFinder(importlib.abc.MetaPathFinder):
    def __init__(self, loader: DbLoader):
        self._loader = loader

    def find_spec(
        self,
        fullname: str,
        path: Sequence[Union[bytes, str]] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if self._loader.provides(fullname):
            spec = importlib.util.spec_from_loader(fullname, self._loader)
            return spec
        return None


def _setup_db(dbhandle):
    with dbhandle:
        dbhandle.execute("""CREATE TABLE code (name, code)""")
        dbhandle.execute(
            """INSERT INTO code VALUES ('my_package.my_module', 'fn = lambda x: x*2')"""
        )


if __name__ == "__main__":
    dbhandle = sqlite3.connect(":memory:")
    _setup_db(dbhandle)
    sys.meta_path.insert(0, DbFinder(DbLoader("my_package", dbhandle)))
    import my_package.does_not_exist
    import my_package.my_module

    print(f"{my_package.my_module.fn(21)=}")
