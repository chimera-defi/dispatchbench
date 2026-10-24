"""Trusted pytest receipt writer; launched with isolated Python outside the candidate repo."""
import json, site, sys
sys.path.append(site.getusersitepackages())  # trusted harness installation, even under -I
import pytest


class Receipt:
    def __init__(self): self.collected = []; self.reports = []; self.deselected = []
    def pytest_collection_finish(self, session): self.collected = [i.nodeid for i in session.items]
    def pytest_deselected(self, items): self.deselected += [i.nodeid for i in items]
    def pytest_runtest_logreport(self, report):
        self.reports.append(dict(id=report.nodeid, when=report.when, outcome=report.outcome, xfail=hasattr(report, "wasxfail")))


if __name__ == "__main__":
    source, output, *args = sys.argv[1:]
    sys.path.insert(0, source)  # import the submitted package, never candidate pytest configuration
    receipt = Receipt()
    code = pytest.main(args, plugins=[receipt])
    with open(output, "w") as f:
        json.dump(dict(collected_ids=receipt.collected, reports=receipt.reports, deselected=receipt.deselected), f)
    sys.exit(code)
