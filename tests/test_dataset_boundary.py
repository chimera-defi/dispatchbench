"""Renderers may read only the cached dataset under results/."""
import ast
import builtins
import io
from pathlib import Path

from analysis import charts, dataset, report


def test_renderers_use_only_dataset(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    for name in ("charts", "page", "report"):
        source = (root / "analysis" / f"{name}.py").read_text()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                assert "summarize" not in (node.module or "").split(".")
                assert all(alias.name != "summarize" for alias in node.names)
            if isinstance(node, ast.Import):
                assert all("summarize" not in alias.name.split(".") for alias in node.names)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert not node.value.endswith(".jsonl"), (name, node.lineno)
                assert not node.value.endswith(".json") or node.value.endswith("dataset.json"), (name, node.lineno)

    # Also catch indirect raw reads through helper modules and dynamically built paths.
    dataset_reads = []
    def guard(original):
        def opened(path, mode="r", *args, **kwargs):
            if isinstance(path, (str, bytes, Path)) and not any(c in mode for c in "wax+"):
                resolved = Path(path).resolve()
                if resolved.is_relative_to(root / "results"):
                    assert resolved == Path(dataset.PATH), f"renderer read {resolved}"
                    dataset_reads.append(resolved)
            return original(path, mode, *args, **kwargs)
        return opened

    monkeypatch.setattr(builtins, "open", guard(builtins.open))
    monkeypatch.setattr(io, "open", guard(io.open))
    charts.build()
    report.render()
    assert len(dataset_reads) == 2  # one snapshot per charts.build()/report.render()
