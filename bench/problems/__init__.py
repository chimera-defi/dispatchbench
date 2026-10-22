"""Problem registry. Each module defines RUNG, FUNC, SIGNATURE, STATEMENT, ref, brute, small, fixed, big, EXAMPLES, WRONG."""
import importlib, pkgutil, os

IDS = sorted(m.name for m in pkgutil.iter_modules([os.path.dirname(__file__)]) if m.name.startswith("p"))


def load(pid):
    return importlib.import_module(f"bench.problems.{pid}")


def path(pid):
    return os.path.join(os.path.dirname(__file__), pid + ".py")


# L1-L6 is the pre-registered ladder ("all"). L7 was added after the main run, because the top configs hit its ceiling (PLAN.md, deviation 16).
MAIN = [p for p in IDS if load(p).RUNG <= 6]
HARD = [p for p in IDS if load(p).RUNG == 7]
