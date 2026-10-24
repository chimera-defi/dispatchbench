export const meta = {
  name: 'page-review',
  description: 'Section-by-section review of the bench report page, plus a consolidation pass; triage; Codex fixes (≤5 turns); re-verify each section',
  whenToUse: 'After the bench report page changes, before republishing it. Args: {repo, url, scratch, sections?, codexTurns?}',
  phases: [
    { title: 'Review', detail: 'one reader per section group + one consolidation reader' },
    { title: 'Triage', detail: 'dedupe, decide, write one fix brief' },
    { title: 'Fix', detail: 'a builder steers Codex sol61 high, at most N turns' },
    { title: 'Verify', detail: 're-check every section against its findings' },
  ],
}

// Defaults match model-routing-bench; override any of them via args.
const A = args || {}
const REPO = A.repo || '<repo>'
const URL = A.url || 'http://127.0.0.1:8765/page.html'
const OUT = A.scratch || `${REPO}/.review`
const TURNS = A.codexTurns || 5
const SECTIONS = A.sections || [
  'top summary, "How it was run", "Problems by round", "Exact commands"',
  '"Cost vs accuracy" (every chart in it) and "Where they fail"',
  '"Results" (verdicts, full table), "Token floor", "Pipelines"',
  '"More charts"/Explorer, Caveats, Code quality, Codex fast mode and xhigh, Appendix',
]

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          section: { type: 'string' },
          severity: { type: 'string', enum: ['wrong', 'confusing', 'polish'] },
          what: { type: 'string', description: 'what a reader sees, quoted' },
          why: { type: 'string' },
          where: { type: 'string', description: 'source file:line that produces it (analysis/*.py, docs/*.tmpl.md, docs/page/*)' },
          fix: { type: 'string' },
        },
        required: ['section', 'severity', 'what', 'why', 'where', 'fix'],
      },
    },
    screenshots: { type: 'array', items: { type: 'string' } },
  },
  required: ['findings', 'screenshots'],
}

const COMMON = `The page is the bench report served at ${URL}, built from ${REPO} (\`make report\`; numbers must pass \`python3 -m analysis.audit\`).
Sources: analysis/page.py (widgets), analysis/report.py, analysis/charts.py, docs/page.tmpl.md (text), docs/page/{style.css,sort.js,shell.html}; data in results/summary.json.
Read-only: do not edit files or call models. Load the Playwright MCP tools via ToolSearch; screenshot at 1280px and 390px wide into ${OUT}/ (prefix files with your section slug).
Every finding names the source file:line that produces it. Skip anything you cannot tie to a reader-visible effect.`

phase('Review')
const reviews = await parallel([
  ...SECTIONS.map((sec, i) => () => agent(
    `Review one part of a report page as a careful first-time reader: ${sec}.\n${COMMON}\n
Check, for every chart, table and paragraph in your part:
1. Does the text say the same thing as the chart/table next to it (counts, sets, which configs, which problems)?
2. Can a reader map every failure to its question? Problems should read "pNN name (Lk)" with the same order and labels everywhere; set names (main ladder L1–L6, L7, hard/rescue set, pilot) should be used consistently.
3. Do the numbers match results/summary.json? Spot-check at least five.
4. Layout: alignment, wrapped lines, overlapping labels, legibility at 390px, light and dark (emulate prefers-color-scheme).
5. Jargon a newcomer would trip on, unexplained abbreviations.`,
    { label: `review:${i + 1}`, phase: 'Review', schema: FINDINGS, agentType: 'reviewer' })),
  () => agent(
    `Consolidation pass over the WHOLE report page: the operator finds maintaining all its charts and tables hard.\n${COMMON}\n
Inventory every chart, table and widget (name, section, the question it answers, its source function, lines of code). Then propose merges and removals:
two views that answer the same question, a table that repeats a chart, an appendix chart nobody needs, hard-coded caption text that restates data (drift risk).
For each proposal: what goes, what absorbs it, what a reader loses (be honest), code lines saved. Report each proposal as a finding with section "consolidation"; severity "polish" unless the duplication already disagrees ("wrong").`,
    { label: 'review:consolidate', phase: 'Review', schema: FINDINGS, agentType: 'reviewer' }),
])
const all = reviews.filter(Boolean).flatMap(r => r.findings)
log(`${all.length} findings from ${reviews.filter(Boolean).length} reviewers`)
if (!all.length) return { findings: 0 }

phase('Triage')
const plan = await agent(
  `You own the fix plan for a report page. Findings from independent reviewers (JSON):\n${JSON.stringify(all)}\n
Repo ${REPO}. Dedupe; verify each "wrong" finding by reading the cited source and summary.json (drop any you cannot confirm, and say so);
accept consolidations whose reader loss is small, reject the rest with a reason. Write ONE brief for Codex to ${OUT}/fix-brief.md:
numbered items, each with file:line, the change, and how to check it. Constraints in the brief: no model calls; do not touch results/*.jsonl or cache/;
\`make report\` then \`python3 -m analysis.audit\` must print OK; \`python3 -m pytest -q tests\` passes; leave changes uncommitted.
Return the brief path, then accepted/rejected counts and one line per rejected item.`,
  { label: 'triage', phase: 'Triage' })

phase('Fix')
const fix = await agent(
  `Steer Codex to apply ${OUT}/fix-brief.md in ${REPO}; you guide and verify, you do not write the fixes.
Turn 1: \`cd ${REPO} && codex exec -m gpt-6.1-sol -c model_reasoning_effort=high -c service_tier=priority -s workspace-write --skip-git-repo-check --json - < ${OUT}/fix-brief.md > ${OUT}/codex-t1.jsonl 2>&1\`; find the thread id in the log;
later turns: \`codex exec resume <thread> -c sandbox_mode=workspace-write ... --json - < nudge.md\`. At most ${TURNS} Codex turns.
After each turn: read git diff, run make report, the audit, the tests; nudge only on real gaps with exact output. Never assert a quota block without the exact error text.
When done, commit yourself (Codex cannot write git metadata) with trailers "Co-authored-by: Chimera <<operator-email>>" and "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
Return: turns used, commit hash, each brief item fixed/partial/not fixed with evidence.`,
  { label: 'fix:codex', phase: 'Fix', agentType: 'builder' })

phase('Verify')
const verdicts = await parallel(SECTIONS.concat(['consolidation (whole page)']).map((sec, i) => () => agent(
  `Re-check a report page after fixes. Your part: ${sec}.\n${COMMON}\n
Findings raised for it before the fix:\n${JSON.stringify(all.filter(f => i < SECTIONS.length ? f.section !== 'consolidation' : f.section === 'consolidation'))}\n
Fix report:\n${fix}\nFor your part only: which findings are now fixed (cite the screenshot), which remain, and anything the fix broke. Severity "wrong" for regressions.`,
  { label: `verify:${i + 1}`, phase: 'Verify', schema: FINDINGS, agentType: 'reviewer' })))
const left = verdicts.filter(Boolean).flatMap(v => v.findings)
return { plan, fix, remaining: left, screenshots: verdicts.filter(Boolean).flatMap(v => v.screenshots) }
