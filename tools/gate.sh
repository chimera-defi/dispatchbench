#!/bin/bash
# golden gate: report + audit + pytest, then tree must equal HEAD (TASKS.md excepted)
cd "$(git rev-parse --show-toplevel)" || exit 9
make report >${TMPDIR:-/tmp}/gate-g-report.log 2>&1 || { echo REPORT-FAIL; exit 1; }
make audit >${TMPDIR:-/tmp}/gate-g-audit.log 2>&1 || { echo AUDIT-FAIL; exit 1; }
python3 -m pytest -q tests >${TMPDIR:-/tmp}/gate-g-pytest.log 2>&1; echo pytest-exit=$?
git diff --exit-code --stat && [ -z "$(git ls-files -o --exclude-standard | grep -vx TASKS.md)" ] && echo GOLDEN-CLEAN || echo GOLDEN-DIRTY
