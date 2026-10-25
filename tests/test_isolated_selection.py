from analysis import dataset, summarize


def test_only_agentic_uses_isolated_rows(monkeypatch):
    original = summarize.load
    def load(path):
        if "2026-10-25-isolated-" in str(path):
            assert str(path).endswith("isolated-agentic.jsonl")
        return original(path)
    monkeypatch.setattr(summarize, "load", load)
    assert summarize.function_rows() == summarize._sourced(summarize.FUNC)
    assert summarize.rescue_rows() == original("results/appendix/luna_rescue.jsonl")
    assert summarize.harness_rows() == original("results/appendix/harness_bias.jsonl")
    raw = original("results/2026-10-25-isolated-agentic.jsonl")
    rows = dataset._rows()
    for config in {r["config"] for r in raw}:
        expected = [r for r in raw if r["config"] == config]
        selected = [r for src, c, st, r in rows if (src, c, st) == ("agentic", config, "repo tasks")]
        assert len(selected) == len(expected)
        assert sum(r["ok"] for r in selected) == sum(r["hidden_pass"] for r in expected)
        assert sum(r["sec"] for r in selected) == sum(r["wall_s"] for r in expected)
        assert sum(r["usd"] for r in selected) == sum(summarize.cost(r) for r in expected)


def test_agentic_selection_rejects_incomplete_cell(monkeypatch):
    import pytest
    original = summarize.load
    rows = original("results/2026-10-25-isolated-agentic.jsonl")[:-1]
    monkeypatch.setattr(summarize, "load", lambda path: rows
                        if str(path).endswith("isolated-agentic.jsonl") else original(path))
    with pytest.raises(AssertionError, match="replacement coverage"):
        summarize.agentic_rows()
