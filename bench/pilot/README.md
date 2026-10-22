# Pilot (2026-10-22), kept as run

These are the scripts that produced `results/2026-10-22-pilot.jsonl` (205 rows) and `results/2026-10-22-pilot-agentic.jsonl` (6 rows). They are kept for provenance and are not used by `make report`. The changes are limited to CLI paths, which now come from `CLAUDE_BIN` and `CODEX_BIN`, and to stderr tails in the data, which had absolute paths replaced with `<path>`.

Known problems with the pilot, all fixed in `bench/` and `PLAN.md`:
- Every run passed, so the pilot shows no failure points.
- The problems are well-known LeetCode tasks (FizzBuzz, Course Schedule II, Candy, Reconstruct Itinerary, Minimum Window Substring, Wildcard Matching), which the models have probably memorised.
- The Codex runs loaded the host's user config and instruction file. That is part of the ~24k-token input floor.
- The Codex priority-tier cost used a 1.5× multiplier. OpenAI's model pages say "Fast mode is priced at 2x the applicable rates". `analysis/` reprices pilot rows at 2×.
- n = 3 per cell, and no confidence intervals.
