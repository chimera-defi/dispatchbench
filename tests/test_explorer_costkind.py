"""G2: each explorer cost surface must explain the row's cost provenance."""
import json
from pathlib import Path
import re
import subprocess

import pytest

from analysis import dataset, page


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cost_surfaces():
    # Use the existing minimal DOM to execute the shipped script. Keep setup
    # outside xfail tests so a broken harness is an ordinary test failure.
    harness = (ROOT / "tests/pareto_runtime.cjs").read_text()
    marker = "const h=context.harness,exp=payload.explorer"
    if marker not in harness:
        pytest.fail("Existing explorer runtime harness entry point changed")
    script = harness.split(marker, 1)[0] + r'''
const {st,render}=context.harness, exp=payload.explorer;
const samples=[];
for(const kind of ['measured','proxy','unmetered']){
 const row=exp.rows.find(r=>r.cost_kind===kind);
 assert(row, `missing ${kind} sample`);
 const set=exp.sets.find(s=>s.rows.includes(row.key));
 st.set=set.id;
 st.off=new Set(set.rows.filter(k=>k!==row.key));
 st.sel=row.key;
 for(const quota of [false,true]){
  st.quota=quota;
  // Unmetered rows must remain labelled in the speed/pass view.
  for(const view of Object.keys(exp.views)){
   if(kind==='unmetered'&&view!=='side')continue;
   st.view=view;render();
   const chart=element('ex-chart').innerHTML;
   const titles=Array.from(chart.matchAll(/<(?:g|path) class="[^"]*ex-point[^>]*>\s*<title>(.*?)<\/title>/gs),m=>m[1]);
   samples.push({kind,quota,view,tooltip:titles,
    detail:element('ex-detail').innerHTML,
    chips:element('ex-best').innerHTML,
    radar:element('ex-radar-grid').innerHTML});
  }
 }
}
console.log(JSON.stringify(samples));
'''
    exp = page.explorer_data(dataset.view(dataset.read()))
    result = subprocess.run(
        ["node", "-e", script], input=json.dumps({"explorer": exp}),
        text=True, capture_output=True, cwd=ROOT,
    )
    if result.returncode:
        pytest.fail(result.stdout + result.stderr)
    samples = json.loads(result.stdout)
    if {s["kind"] for s in samples} != {"measured", "proxy", "unmetered"}:
        pytest.fail("Runtime harness did not exercise every cost kind")
    if not all(s["tooltip"] for s in samples):
        pytest.fail("Runtime harness did not capture point tooltips in every view")
    return samples


@pytest.mark.xfail(
    strict=True, raises=AssertionError,
    reason="G2: explorer cost labels need analysis/page.py and docs/page/explorer.html fixes; both are outside S3 scope",
)
@pytest.mark.parametrize("surface", ["tooltip", "detail", "chips", "radar"])
def test_every_explorer_cost_surface_labels_cost_kind(cost_surfaces, surface):
    labels = {
        "measured": r"\bmeasured\b",
        "proxy": r"token[ -]estimate|estimated from tokens",
        "unmetered": r"\bunmetered\b",
    }
    for sample in cost_surfaces:
        texts = sample[surface]
        if isinstance(texts, str):
            texts = [texts]
        for text in texts:
            assert re.search(labels[sample["kind"]], text, re.I), (
                surface, sample["kind"], sample["quota"], sample["view"], text,
            )
