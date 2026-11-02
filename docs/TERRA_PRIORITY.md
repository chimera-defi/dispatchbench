# gpt-6.1-terra at the priority tier: verdict (exploratory)

Run 2026-11-02 under PLAN.md deviation 25. All rows are exploratory. Numbers are in [results/report/terra_priority.md](../results/report/terra_priority.md),
rebuilt by `make report` from `results/2026-11-02-terra-*.jsonl` (raw rows indexed in [RAW_RUNS.md](RAW_RUNS.md)). Codex costs are list-price estimates, ⚡ at 2×.

## Answers

1. **Is terra61-low vs terra61-high (60/60 vs 58/60) real? No, it is noise.** Standard tier, 15 repeats each (180 calls): low 179/180, high 177/180.
   The difference is +1.1 points, 95% interval −1.6 to +4.3, Fisher p = 0.62. The new repeats 6–15 alone were 119/120 each.
   Per the reading rule, no effort level wins on pass rate. Low is a little faster (median 7.4 s vs 9.2 s pooled) at the same cost per pass ($0.0069 vs $0.0065).
2. **Priority tier does not change accuracy and cuts wall time by about 40%.** Function track, 5 repeats: terra61-low ⚡ 60/60 at 6.0 s median, terra61-high ⚡ 58/60 at 6.9 s.
   The two high misses repeat the standard-tier ones, both on p04 (wrong answers).
3. **Repo track, hidden suites, 4 tasks × 5 repeats, all ⚡:** terra61-low 20/20 (median 30 s, $0.060 per complete task), terra61-high 20/20 (28 s, $0.064), sol61-high 20/20 (53 s, $0.18).
   No test tampering. The earlier standard-tier sol61-high repo rows were 12/12 at 109 s.

## Is terra61 a better default delegation model than sol61-high ⚡?

| Function track p01–p12, ⚡ | pass | median s | $ per pass |
|---|---|---|---|
| sol61-high ⚡ (current default) | 60/60 | 17.4 | $0.036 |
| terra61-low ⚡ | 60/60 | 6.0 | $0.011 |
| terra61-high ⚡ | 58/60 | 6.9 | $0.012 |

- **Wall time:** terra61 ⚡ is about 2.5–3× faster on the function track and about 1.8× on repo tasks.
- **Cost per pass:** about 3× lower on both tracks.
- **Pass rate:** no measured difference on the sets run. Every interval overlaps: 100% at 60/60 means the lower bound is 94.0%, and 20/20 means 83.9%.
- **Effort:** terra61-low. High adds time and no measured accuracy.

**Recommendation:** terra61-low ⚡ is the better default for routine delegated builds, on speed and cost at equal measured pass rate. Keep sol61-high ⚡ for work the bench has not covered.

## Caveats

- **Weak spot:** terra61 misses are concentrated on p04 (taller_within, bounded-window search): 14/15 low and 12/15 high at standard tier, 5/5 and 3/5 at ⚡, against 10/10 for sol61-high and 5/5 for sol61-high ⚡. At 5–15 repeats per problem, a 5–20 point gap on one hard problem is not ruled out.
- **Not run for terra61:** the L7 hard set (p13–p15) and repo tasks at the standard tier. Sol61-high has both.
- **Repo track is small:** 4 tasks, 20 tries per config. Zero failures means the pass rate is at least 83.9%, not that it is 100%. Repo wall times were taken on a loaded host (load average about 20, with grading running in parallel at the start), so read them as indicative. Function ⚡ and noise rows ran as two jobs of 2 lanes (4 calls in flight), the earlier rows as one job of 4 lanes, so the timing load is similar but not identical.
- **Cost:** list-price estimates from token counts. Terra ⚡ cost per pass is only about 1.6× the standard-tier figure, not 2×, because token use varied between runs (the first 5 standard repeats were pricier than the pooled 15).
- The main report page and its template claims (for example "astra-medium fast is the fastest config with no misses") were not edited. terra61-low ⚡ at 6.0 s would falsify that line, so the ⚡ rows are kept out of the page's data sources until someone rewrites it deliberately.
