"""One data file feeds everything: results/dataset.json is derived from results/*.jsonl by script, and renderers read only it."""
import ast, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
# Modules that may open results/*.jsonl: dataset.py and what it imports for computation. export_solutions.py exports code, not numbers.
LOADERS = {"dataset.py", "summarize.py", "fast_gate.py", "harness_bias.py", "luna_rescue.py", "rawindex.py", "export_solutions.py"}
RENDERERS = {"page.py", "charts.py", "report.py", "grok.py", "raw_runs.py", "audit.py", "og.py", "labels.py"}
PATHLIKE = re.compile(r"[\w\-/]\.jsonl\b|summary\.json\b")  # a file name, not the bare word in prose ("without `.jsonl`")


def string_constants(path):
    tree = ast.parse(path.read_text())
    return [(n.lineno, n.value) for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def test_renderers_never_name_a_jsonl_or_summary_json():
    bad = []
    for name in sorted(RENDERERS):
        for line, value in string_constants(ANALYSIS / name):
            if PATHLIKE.search(value): bad.append(f"analysis/{name}:{line}: {value[:70]!r}")
    assert not bad, "renderers must read results/dataset.json only:\n" + "\n".join(bad)


def test_every_analysis_module_is_classified():
    """A new analysis module has to say whether it loads or renders; test files and the registry modules are exempt."""
    exempt = {"__init__.py", "configs.py", "stats.py", "landcheck.py", "agentic_tests.py", "problem_notes.py"}
    mods = {p.name for p in ANALYSIS.glob("*.py") if not p.name.startswith("test_")}
    assert mods - LOADERS - RENDERERS - exempt == set()


def test_loaders_are_the_only_modules_that_open_a_jsonl():
    """Everything else in analysis/ (tests aside) must contain no .jsonl file name at all except the registry that lists run files."""
    offenders = []
    for p in ANALYSIS.glob("*.py"):
        if p.name.startswith("test_") or p.name in LOADERS or p.name in {"configs.py", "landcheck.py", "agentic_tests.py"}: continue
        for line, value in string_constants(p):
            if PATHLIKE.search(value): offenders.append(f"{p.name}:{line}")
    assert offenders == []


# ---------- derived data: facts, rows, rules, design, annotations ----------
import hashlib, json, subprocess
import pytest
from analysis import audit, dataset, report

DS = ROOT / "results" / "dataset.json"
PAGE = ROOT / "results" / "report" / "page.html"


@pytest.fixture(scope="module")
def ds():
    return json.loads(DS.read_text())


def test_generated_from_lists_every_jsonl_with_its_hash_and_row_count(ds):
    on_disk = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "results").rglob("*.jsonl"))
    assert [g["path"] for g in ds["generated_from"]] == on_disk
    for g in ds["generated_from"]:
        path = ROOT / g["path"]
        assert g["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), g["path"]
        assert g["rows"] == sum(1 for line in path.read_text().splitlines() if line.strip()), g["path"]
    assert any(g["used"] for g in ds["generated_from"])


def test_every_fact_is_value_unit_display_source(ds):
    assert ds["facts"]
    for k, f in ds["facts"].items():
        assert set(f) == {"value", "unit", "display", "source"}, k
        assert f["source"], k


def test_every_pass_count_names_its_rule(ds):
    """Rows, the rescue arms and the derived pipelines: a pass count without a rule fails."""
    assert dataset.RULES == ("function tests (reference + brute force)", "hidden tests", "task_complete")
    for r in ds["rows"]:
        if r["set"] == "repo tasks":
            # one headline rule: task complete; the hidden-suite count rides beside it
            assert r["rule"] == "task_complete" and r["hidden_rule"] == "hidden tests" and "hidden_pass" in r and "task_complete" in r, r["id"]
            assert r["passes"] == r["task_complete"] and r["hidden_pass"] >= r["passes"], r["id"]
        else:
            assert r["rule"] in dataset.RULES[:2], r["id"]
            assert "task_complete" not in r or r["source"] == "agentic", r["id"]
    for name, v in ds["rescue"].items(): assert v["rule"] in dataset.RULES, name
    for cfg, groups in ds["derived_pipelines"].items():
        for g, v in groups.items(): assert v["rule"] in dataset.RULES, (cfg, g)
    for c, v in ds["grok_repository"]["metrics"].items(): assert v["rule"] == "task_complete" and v["hidden_rule"] == "hidden tests", c


def test_rendered_pass_columns_and_repo_cells_name_their_rule(ds):
    for name, spec in ds["tables"].items():
        if not isinstance(spec, dict): continue
        for h in spec["head"]:
            if dataset.PASS_HEAD.search(h):
                assert any(w in h for w in ("function tests", "hidden", "task complete")), (name, h)
    for row in ds["tables"]["agentic"]["rows"]:
        assert re.search(r"\d+/\d+ complete \(\d+/\d+ hidden\)", row[1]), row  # the one marker: task complete first, hidden beside it
    assert "task_complete" in ds["tables"]["grok_repository"]


def test_two_labelled_repo_columns_never_merge(ds):
    head = ds["tables"]["agentic"]["head"]
    assert any("hidden" in h for h in head) and any("task complete" in h for h in head)


def test_design_constants_match_the_code_they_are_read_from(ds):
    consts = ds["design"]["constants"]
    assert consts
    for k, c in consts.items():
        assert c["source"] and c["display"], k
        if "pin" in c:
            file, pattern = c["pin"]
            assert re.search(pattern, (ROOT / file).read_text()), f"{k}: {file} no longer holds {pattern}"
    assert consts["brute_inputs"]["value"] == 2000 and consts["esc_max"]["value"] == 2


def test_annotations_file_is_audit_owned_and_well_formed(ds):
    ann = json.loads((ROOT / "results" / "annotations.json").read_text())
    assert ds["annotations"] == ann
    for run_id, a in ann.items():
        assert set(a) == {"label", "note", "decided_by", "date"}, run_id


def test_unlabelled_red_run_shows_under_audit_and_a_label_clears_it(tmp_path, monkeypatch, ds):
    red = [x for r in ds["rows"] for x in r.get("red_runs", [])]
    assert red, "the isolated rerun has red-suite luna-low runs"
    monkeypatch.setattr(dataset, "ANNOTATIONS", str(tmp_path / "none.json"))
    assert dataset.audit_mark(red) == " (under audit)"
    assert "Red-suite runs" in dataset.audit_footnote(red)
    labelled = tmp_path / "ann.json"
    labelled.write_text(json.dumps({r: {"label": "x", "note": "", "decided_by": "audit", "date": "2026-10-28"} for r in red}))
    monkeypatch.setattr(dataset, "ANNOTATIONS", str(labelled))
    assert dataset.audit_mark(red) == ""
    assert "carries an audit label" in dataset.audit_footnote(red)


# ---------- templates: no hand-typed figure ----------
def test_templates_hold_no_digit_outside_a_token_or_an_allowed_category():
    allow = json.loads((ROOT / "docs" / "audit_allow.json").read_text())
    assert all(a["reason"] and a["name"] for a in allow)
    stray, used = audit.stray_literals(audit.template_literals(), allow)
    assert stray == []
    assert used == set(range(len(allow))), "an allowed category matches nothing: remove it"


@pytest.mark.parametrize("name", ["report.tmpl.md", "page.tmpl.md", "readme.tmpl.md"])
def test_a_stray_number_in_a_template_is_caught(tmp_path, name):
    allow = json.loads((ROOT / "docs" / "audit_allow.json").read_text())
    copy = tmp_path / name
    copy.write_text((ROOT / "docs" / name).read_text() + "\nThe run cost 17 dollars.\n")
    stray, _ = audit.stray_literals(audit.template_literals([str(copy)]), allow)
    assert any("literal '17'" in s for s in stray)
    copy.write_text((ROOT / "docs" / name).read_text() + "\nThe run cost {{claude_usd}} and took 12:30 minutes.\n")
    stray, _ = audit.stray_literals(audit.template_literals([str(copy)]), allow)
    assert any("literal '12'" in s or "literal '30'" in s for s in stray) and not any("'17'" in s for s in stray)


def test_a_stray_number_in_the_page_html_is_caught(tmp_path):
    allow = json.loads((ROOT / "docs" / "audit_allow.json").read_text())
    copy = tmp_path / "explorer.html"
    copy.write_text((ROOT / "docs" / "page" / "explorer.html").read_text() + "<p>Pass rate 83% overall</p>")
    stray, _ = audit.stray_literals(audit.template_literals([str(copy)]), allow)
    assert any("literal '83'" in s for s in stray)


# ---------- the page: embedded data, no JS aggregation ----------
def page_text():
    return PAGE.read_text()


def test_page_embeds_its_data_block_and_every_visible_number_is_in_it():
    page = page_text()
    block = audit.DATA_BLOCK.search(page)
    assert block, "the page must embed <script type=application/json id=data>"
    data = json.loads(block.group(1))
    assert {"facts", "rows", "tables", "charts", "widgets", "explorer"} <= set(data)
    allow = json.loads((ROOT / "docs" / "audit_allow.json").read_text())
    assert audit.page_numbers_missing(page, allow) == []
    assert audit.page_numbers_missing(page.replace("<main>", "<main><p>It took 98765 s</p>", 1), allow) == ["page: number 98765 is visible but not in the embedded data block"]


def test_the_explorer_reads_its_numbers_from_the_data_block():
    body = page_text()
    assert "JSON.parse(document.getElementById(\"data\").textContent).explorer" in body
    assert "__DATA__" not in body and "__USD_TICKS__" not in body and "__FLOOR_OPTIONS__" not in body
    assert ".05*b" not in body and "Math.min(.5" not in body, "the tie rule comes from design.explorer.tie"


def test_page_javascript_does_no_aggregation_over_rows():
    scripts = re.findall(r"<script(?![^>]*application/json)[^>]*>(.*?)</script>", page_text(), re.S)
    assert scripts
    for js in scripts:
        # label placement sums pixel overlaps of boxes on screen, which is layout geometry and no figure from the data
        js = re.sub(r"\.reduce\(function\(s,q\)\{return s\+overlap\([^;]*?\)\}\s*,\s*0\)", "", js)
        assert ".reduce(" not in js, "sum or average in JS: move it into dataset.py"
        assert not re.search(r"/\s*[\w.\]\[]+\.length\b", js), "mean over rows in JS: move it into dataset.py"
        assert not re.search(r"\.length\s*\)?\s*/", js)
    sources = (ROOT / "docs" / "page" / "sort.js").read_text() + (ROOT / "docs" / "page" / "explorer.html").read_text()
    assert ".reduce(" not in sources


def test_summary_json_is_gone_and_no_renderer_input():
    assert not (ROOT / "results" / "summary.json").exists()
