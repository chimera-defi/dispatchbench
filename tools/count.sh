#!/bin/bash
# Line counts, same counter as phase 1 (data excluded). Bytes too, because these files have very long lines.
cd "$(git rev-parse --show-toplevel)" || exit 9
data='bench/problems|bench/agentic/tasks|bench/pilot/agentic|docs/page/design-system|^results|^cache'
code=$(git ls-files 'bench/*.py' 'analysis/*.py' 'tools/*' 'Makefile' | grep -v -E "$data" | grep -v -E 'test_|conftest')
docs=$(git ls-files '*.md' 'docs/*.json' | grep -v -E '^results|^cache|design-system')
echo "code=$(cat $code | wc -l) lines, $(cat $code | wc -c) bytes"
echo "tests=$(git ls-files 'tests/*' | xargs cat | wc -l)"
echo "pagesrc=$(git ls-files 'docs/page/*' | grep -v design-system | xargs cat | wc -l)"
echo "docs=$(cat $docs | wc -l) (generated: $(cat docs/REPORT.md README.md docs/RAW_RUNS.md | wc -l))"
