# Does the harness family bias results? (full pre-registered run, n=60 per cell)

**Answer: NOT 'yes' under the rule (CI excludes 0 but D fails the D > 0 and D >= 0.15 test).**

D = +0.133, 95% CI [+0.033, +0.233]  (D>0 would mean Codex harness favours Codex model).

| | Claude harness (one-shot) | Codex harness (tool loop) |
|---|---|---|
| luna-low (Codex family) | 36/60 pass, $0.047, 7.5s | 47/60 pass, $0.187, 21.1s |
| haiku-low (Claude family) | 57/60 pass, $0.144, 13.6s | 60/60 pass, $0.161, 13.6s |

Cells: pass count / calls, total $, median wall seconds. 6 problems x 10 fresh repeats (11-20) per cell, n=60 per cell, 240 calls. This is the full pre-registered run.
`harness_error` rows: 0 ({'claude-one-shot/luna-low': 0, 'claude-one-shot/haiku-low': 0, 'codex-tool-loop/luna-low': 0, 'codex-tool-loop/haiku-low': 0}); counted as fails above.
Calls with no cost figure: 0. Incomplete pairs dropped: 0.

Secondary (interaction on mean log): cost D = +1.200 CI [+1.108, +1.292]; wall D = +1.176 CI [+1.081, +1.275]. A secondary hit (log_cost, log_wall) means the harness changes cost/latency rankings, not bias.
Note: Codex-model $ is a list-price proxy, Claude-model $ is measured, in both harnesses.

Drift check (10-22 Claude-harness rows, 6 problems x 5 repeats): luna-low 16/30, haiku-low 27/30 pass.

**Confound:** the harnesses differ in mechanism (one-shot vs tool loop with code execution), not just in who wrote them. A positive D could be mechanism x model, not family loyalty. The prompt-swap ablation within each style runs only if D is positive.

Method: pairs by (problem, repeat); bootstrap 10,000 resamples of pairs stratified by problem, 95% percentile CI; seed 1.

Reproduce:
```
P=p03_ledger,p04_taller_within,p08_recur,p09_k_machine_schedule,p11_best_average,p12_sheet
for r in $(seq 11 20); do
  python3 -m bench.run --phase harness_bias --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2 &
  python3 -m bench.codex_harness --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2
  wait
done
python3 -m analysis.harness_bias
```
