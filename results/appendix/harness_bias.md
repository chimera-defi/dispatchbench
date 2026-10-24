# Does the harness family bias results? (underpowered subset, n=18 per cell)

**Answer: NO bias of about 0.3 or more is detectable (CI contains 0). This is not 'no bias'.**

D = +0.111, 95% CI [-0.056, +0.278]  (D>0 would mean Codex harness favours Codex model).

| | Claude harness (one-shot) | Codex harness (tool loop) |
|---|---|---|
| luna-low (Codex family) | 11/18 pass, $0.014, 7.3s | 14/18 pass, $0.065, 21.9s |
| haiku-low (Claude family) | 17/18 pass, $0.044, 15.1s | 18/18 pass, $0.049, 14.0s |

Cells: pass count / calls, total $, median wall seconds. 6 problems x 3 fresh repeats (11-13) per cell, n=18 per cell, 72 calls. Scope cut from the pre-registered 10 repeats; treat as underpowered subset.
`harness_error` rows: 0 ({'claude-one-shot/luna-low': 0, 'claude-one-shot/haiku-low': 0, 'codex-tool-loop/luna-low': 0, 'codex-tool-loop/haiku-low': 0}); counted as fails above.
Calls with no cost figure: 0. Incomplete pairs dropped: 0.

Secondary (interaction on mean log): cost D = +1.393 CI [+1.264, +1.524]; wall D = +1.386 CI [+1.215, +1.567]. A secondary hit (log_cost, log_wall) means the harness changes cost/latency rankings, not bias.
Note: Codex-model $ is a list-price proxy, Claude-model $ is measured, in both harnesses.

Drift check (10-22 Claude-harness rows, 6 problems x 5 repeats): luna-low 16/30, haiku-low 27/30 pass.

Codex harness ran the six hard problems with 0 harness errors, no timeouts, in about 3 minutes per repeat block, so it reproduced our setup without trouble. Problem set used: p03, p04, p08, p09, p11, p12 (no fallback to the pilot set). Whole run: about 13 minutes wall.

**Confound:** the harnesses differ in mechanism (one-shot vs tool loop with code execution), not just in who wrote them. A positive D could be mechanism x model, not family loyalty. The prompt-swap ablation within each style runs only if D is positive.

Method: pairs by (problem, repeat); bootstrap 10,000 resamples of pairs stratified by problem, 95% percentile CI; seed 1.

Reproduce:
```
P=p03_ledger,p04_taller_within,p08_recur,p09_k_machine_schedule,p11_best_average,p12_sheet
for r in 11 12 13; do
  python3 -m bench.run --phase harness_bias --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2 &
  python3 -m bench.codex_harness --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2
  wait
done
python3 -m analysis.harness_bias
```
