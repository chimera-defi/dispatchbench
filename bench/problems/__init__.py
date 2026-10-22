"""Problem registry. Each module defines RUNG, FUNC, SIGNATURE, STATEMENT, ref, brute, small, fixed, big, EXAMPLES, WRONG."""
import importlib, pkgutil, os

IDS = sorted(m.name for m in pkgutil.iter_modules([os.path.dirname(__file__)]) if m.name.startswith("p"))


def load(pid):
    return importlib.import_module(f"bench.problems.{pid}")


def path(pid):
    return os.path.join(os.path.dirname(__file__), pid + ".py")
