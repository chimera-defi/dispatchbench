## 1. Function track, priority tier (⚡), p01–p12, repeats 1–5

| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list, ⚡ ×2) | infra errors |
|---|---|---|---|---|---|---|
| terra61-low (standard) | 60/60 | 100.0% (94.0%–100.0%) | 10.3 | 20.8 | $0.010 | 0 |
| terra61-low ⚡ | 60/60 | 100.0% (94.0%–100.0%) | 6.0 | 8.2 | $0.011 | 0 |
| terra61-high (standard) | 58/60 | 96.7% (88.6%–99.1%) | 11.9 | 19.5 | $0.0079 | 0 |
| terra61-high ⚡ | 58/60 | 96.7% (88.6%–99.1%) | 6.9 | 9.8 | $0.012 | 0 |
| sol61-high (standard) | 60/60 | 100.0% (94.0%–100.0%) | 27.4 | 49.7 | $0.019 | 0 |
| sol61-high ⚡ | 60/60 | 100.0% (94.0%–100.0%) | 17.4 | 27.8 | $0.036 | 0 |

## 2. Noise check, standard tier: terra61-low vs terra61-high

Reading rule (PLAN.md deviation 25): if the Newcombe interval for the difference contains 0 the gap is noise and no effort level wins on pass rate.

| set | terra61-low | terra61-high | low − high (95% Newcombe) | Fisher p |
|---|---|---|---|---|
| original repeats 1–5 | 60/60 (100.0%; 94.0%–100.0%) | 58/60 (96.7%; 88.6%–99.1%) | +3.3 pts (-3.2 to +11.4) | 0.496 |
| new repeats 6–15 | 119/120 (99.2%; 95.4%–99.9%) | 119/120 (99.2%; 95.4%–99.9%) | +0.0 pts (-3.8 to +3.8) | 1.000 |
| pooled 1–15 | 179/180 (99.4%; 96.9%–99.9%) | 177/180 (98.3%; 95.2%–99.4%) | +1.1 pts (-1.6 to +4.3) | 0.623 |

| pooled 1–15 | median s | slow-call s | $ per pass (list) |
|---|---|---|---|
| terra61-low | 7.4 | 15.0 | $0.0069 |
| terra61-high | 9.2 | 19.4 | $0.0065 |

Every terra61 main-ladder miss in the deviation-25 comparison sets (config, problem, repeat, outcome): ('terra61-high', 'p04_taller_within', 1, 'wrong'); ('terra61-high', 'p04_taller_within', 3, 'wrong'); ('terra61-high', 'p04_taller_within', 8, 'wrong'); ('terra61-high-fast', 'p04_taller_within', 3, 'wrong'); ('terra61-high-fast', 'p04_taller_within', 4, 'wrong'); ('terra61-low', 'p04_taller_within', 10, 'wrong').

## 3. Repo track (4 tasks, hidden suites)

| config | task complete | hidden pass | median s | $ per complete task (list, ⚡ ×2) | misses (task, repeat) |
|---|---|---|---|---|---|
| terra61-low-fast ⚡ | 20/20 (100.0%; 83.9%–100.0%) | 20/20 | 30 | $0.060 | none |
| terra61-high-fast ⚡ | 20/20 (100.0%; 83.9%–100.0%) | 20/20 | 28 | $0.064 | none |
| sol61-high-fast ⚡ | 20/20 (100.0%; 83.9%–100.0%) | 20/20 | 53 | $0.18 | none |
| sol61-high (standard, earlier rows) | 12/12 (100.0%; 75.8%–100.0%) | 12/12 | 109 | $0.095 | none |

## 4. Follow-up: L7, standard tier (exploratory, deviation 26)

Terra p13–p15 repeats 1–5 against existing sol61-high L7 repeats 1–5. Function-test grading is unchanged.

| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list) | infra errors |
|---|---|---|---|---|---|---|
| terra61-low | 14/15 | 93.3% (70.2%–98.8%) | 8.6 | 11.9 | $0.0057 | 0 |
| terra61-high | 15/15 | 100.0% (79.6%–100.0%) | 11.7 | 13.5 | $0.0059 | 0 |
| sol61-high | 15/15 | 100.0% (79.6%–100.0%) | 52.7 | 76.9 | $0.024 | 0 |

## Follow-up: L7 at priority tier (deviation 27)

| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list, ⚡ ×2) | infra errors |
|---|---|---|---|---|---|---|
| terra61-low ⚡ | 14/15 | 93.3% (70.2%–98.8%) | 7.1 | 8.0 | $0.015 | 0 |

## 5. Follow-up: repo track, standard tier (exploratory, deviation 26)

Terra t1–t4 repeats 1–5 against earlier default-tier sol61-high repeats 1–3. Cached hidden-suite verdicts; task complete requires visible and hidden passes.

| config | task complete | hidden pass | median s | $ per complete task (list) | misses (task, repeat) |
|---|---|---|---|---|---|
| terra61-low | 20/20 (100.0%; 83.9%–100.0%) | 20/20 | 34.5 | $0.029 | none |
| terra61-high | 20/20 (100.0%; 83.9%–100.0%) | 20/20 | 36.0 | $0.032 | none |
| sol61-high | 12/12 (100.0%; 75.8%–100.0%) | 12/12 | 108.6 | $0.095 | none |

## 6. Follow-up: p04 weak spot, all standard-tier rows (exploratory, deviation 26)

Terra repeats 1–35; Sol repeats 1–30, including standard-tier phase=fastmode control repeats 6–10. Distinct call keys only; priority configs excluded.

| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list) | infra errors |
|---|---|---|---|---|---|---|
| terra61-low | 34/35 | 97.1% (85.5%–99.5%) | 5.1 | 7.3 | $0.0035 | 0 |
| terra61-high | 29/35 | 82.9% (67.3%–91.9%) | 5.4 | 6.7 | $0.0046 | 0 |
| sol61-high | 30/30 | 100.0% (88.6%–100.0%) | 18.0 | 24.0 | $0.010 | 0 |

terra61-low − sol61-high: -2.9 points; 95% Newcombe interval -14.5 to +8.7 points. Per the fixed reading rule, the p04 weak spot is **not established as real** (the interval contains 0).

## 7. Deviation-26 spend (list price)

90 new function calls + 40 repo runs: L7 $0.167936, repo $1.209178, p04 $0.341893; total **$1.719007** against the $6 cap ($4.280993 remaining). Earlier comparison rows are excluded. Token prices come from results/prices.json, with cached-input discounts; every new row is default tier.
