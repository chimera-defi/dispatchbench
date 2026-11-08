#!/bin/bash
# golden gate: report + audit + pytest, then tree must equal HEAD (TASKS.md excepted)
cd "$(git rev-parse --show-toplevel)" || exit 9
make report >${TMPDIR:-/tmp}/gate-g-report.log 2>&1 || { echo REPORT-FAIL; exit 1; }
make audit >${TMPDIR:-/tmp}/gate-g-audit.log 2>&1 || { echo AUDIT-FAIL; exit 1; }
python3 -m pytest -q tests >${TMPDIR:-/tmp}/gate-g-pytest.log 2>&1; echo pytest-exit=$?
git diff --exit-code --stat && [ -z "$(git ls-files -o --exclude-standard | grep -vx TASKS.md)" ] && echo GOLDEN-CLEAN || echo GOLDEN-DIRTY
# gate compares to HEAD, so also pin every output to the phase-2 baseline; fails if a commit changed the golden
git diff --quiet 7e946a6 HEAD -- results/report results/dataset.json results/manifest.json README.md docs/REPORT.md docs/RAW_RUNS.md results/solutions && echo BASELINE-SAME || echo BASELINE-CHANGED
