from analysis import configs, dataset, summarize


def test_only_agentic_uses_isolated_rows(monkeypatch):
    original = summarize.load
    def load(path):
        if "2026-10-25-isolated-" in str(path):
            assert str(path).endswith("isolated-agentic.jsonl")
        return original(path)
    monkeypatch.setattr(summarize, "load", load)
    function_rows = summarize.function_rows()
    assert [r for r in function_rows if r["config"] not in configs.GROK_CONFIGS and r["_file"] == "results/2026-10-22b-function.jsonl"] == summarize._sourced(summarize.FUNC)
    assert [r for r in function_rows if r["config"] in configs.GROK_CONFIGS] == (
        summarize._sourced(f"{summarize.RES}/2026-10-26-grok-function.jsonl")
        + summarize._sourced(f"{summarize.RES}/2026-10-28-grok-spectrum-function.jsonl"))
    assert [r for r in function_rows if r["_file"] == "results/2026-10-28-terra-function.jsonl"] == summarize._sourced(
        f"{summarize.RES}/2026-10-28-terra-function.jsonl")
    assert summarize.rescue_rows() == original("results/appendix/luna_rescue.jsonl")
    assert summarize.harness_rows() == original("results/appendix/harness_bias.jsonl")
    raw = original("results/2026-10-25-isolated-agentic.jsonl")
    rows = dataset._rows()
    for config in {r["config"] for r in raw}:
        expected = [r for r in raw if r["config"] == config]
        selected = [r for src, c, st, r in rows if (src, c, st) == ("agentic", config, "repo tasks")]
        assert len(selected) == len(expected)
        assert sum(r["ok"] for r in selected) == sum(bool(r["task_complete"]) for r in expected)  # the headline repo-task rule: task complete
        assert sum(r["hid"] for r in selected) == sum(r["hidden_pass"] for r in expected)  # the hidden suite alone, kept beside it
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
