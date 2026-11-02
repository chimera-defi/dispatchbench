# gpt-6.1-terra at the priority tier: verdict (exploratory)

Run 2026-11-02 under PLAN.md deviations 25 and 26. All rows are exploratory. Numbers are in [results/report/terra_priority.md](../results/report/terra_priority.md),
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

- **Weak spot p04 (taller_within, bounded-window search): not established as real under the fixed reading rule.** Earlier standard-tier counts were 14/15 low, 12/15 high and 10/10 sol61-high; the ⚡ counts remain 5/5, 3/5 and 5/5 respectively. With deviation 26, all standard-tier p04 rows give low **34/35** (97.1%; 95% Wilson 85.5%–99.5%), high **29/35** (82.9%; 67.3%–91.9%) and sol61-high **30/30** (100%; 88.6%–100%). Low minus Sol is −2.9 points, 95% Newcombe **−14.5 to +8.7 points**; the interval contains 0, so the specified comparison does not establish a real weak spot.
- **L7 and standard-tier repo now run (deviation 26):** L7 p13–p15, 5 repeats: terra61-low 14/15 (median 8.6 s, $0.0057 per pass), terra61-high 15/15 (11.7 s, $0.0059), against existing sol61-high 15/15 (52.7 s, $0.024). Low missed p15 repeat 3 (wrong answer). Standard-tier repo: low 20/20 complete and hidden-pass (34.5 s, $0.029 per complete task), high 20/20 (36.0 s, $0.032), against earlier sol61-high 12/12 (108.6 s, $0.095). Neither Terra arm tampered with tests. These are exploratory comparisons over only 3 hard problems and 4 repo tasks; they do not establish equal population pass rates.
- **Repo track is small:** 4 tasks, 20 tries per config. Zero failures means the pass rate is at least 83.9%, not that it is 100%. Repo wall times were taken on a loaded host (load average about 20, with grading running in parallel at the start), so read them as indicative. Function ⚡ and noise rows ran as two jobs of 2 lanes (4 calls in flight), the earlier rows as one job of 4 lanes, so the timing load is similar but not identical.
- **Cost:** list-price estimates from token counts. Terra ⚡ cost per pass is only about 1.6× the standard-tier figure, not 2×, because token use varied between runs (the first 5 standard repeats were pricier than the pooled 15).
- The two priority-tier function arms (p01–p12, repeats 1–5) are now on the main report page, with 60 tries each. Its fastest-no-miss claim now comes from computed facts: terra61-low ⚡. Noise, follow-up and priority-tier repo rows remain outside the main-ladder data; sol61-high ⚡ stays the Default pick under the every-set, every-try rule.

Deviation 26 spent **$1.719007** at list price: L7 $0.167936, standard-tier repo $1.209178, p04 $0.341893, below the $6 cap. This counts only the 90 new function calls and 40 repo runs, excluding earlier comparison rows. The follow-up rows also stay outside the main-page data sources and dollar charts.

Superseded by deviation 26: the original p04 sample-size caution (5–15 repeats) and the sentence “Not run for terra61: the L7 hard set (p13–p15) and repo tasks at the standard tier.” The earlier counts, priority-tier results, noise-check findings and recommendation are retained. The generated appendix’s earlier miss list is now explicitly scoped to its deviation-25 comparison sets.
