export const meta = {
  name: 'page-converge',
  description: 'Loop until dry: check every operator request + ADHD readability on the report page, Codex fixes, re-check; stop after 2 clean rounds or maxRounds',
  whenToUse: 'After page changes land, before republishing. Args: {repo, url, scratch, ledger, maxRounds?, codexTurns?}',
  phases: [
    { title: 'Check', detail: 'request ledger + ADHD readability + charts, in parallel' },
    { title: 'Fix', detail: 'a builder steers Codex sol61 high' },
  ],
}

const A = args || {}
const REPO = A.repo || '<repo>'
const URL = A.url || 'http://127.0.0.1:8765/page.html'
const OUT = A.scratch || `${REPO}/.review/converge`
const LEDGER = A.ledger
const MAX = A.maxRounds || 3
const TURNS = A.codexTurns || 3

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          key: { type: 'string', description: 'stable id, e.g. "req2:pareto-legend" or "adhd:winner-lead"' },
          severity: { type: 'string', enum: ['missing', 'wrong', 'confusing', 'polish'] },
          what: { type: 'string' },
          where: { type: 'string', description: 'source file:line' },
          fix: { type: 'string' },
        },
        required: ['key', 'severity', 'what', 'where', 'fix'],
      },
    },
  },
  required: ['findings'],
}

const COMMON = `Page: ${URL}, built from ${REPO} by \`make report\` (sources analysis/page.py, analysis/report.py, analysis/charts.py, docs/page.tmpl.md, docs/page/*). Read-only: edit nothing, call no models.
Load Playwright via ToolSearch; check at 1280px and 390px, light and dark; screenshots go to ${OUT}/. Report only reader-visible problems, each tied to a source file:line. Skip "polish" unless it hurts reading.`

const LENSES = [
  { k: 'ledger', p: `Go through the operator's request ledger at ${LEDGER}. For EACH item, decide whether it is visibly true on the page. Anything not done is "missing" (key "reqN:..."); anything partly done is "wrong". Quote what you see.` },
  { k: 'adhd', p: `Read the page as a reader with ADHD. Rules: every section opens with its takeaway in one line; key numbers are not buried in paragraphs; steps are numbered; sentences are short; no jargon or abbreviation is left unexplained; wins are visible; nothing asks the reader to remember something from elsewhere on the page. Flag violations (key "adhd:...") with the rewritten text as the fix.` },
  { k: 'charts', p: `Check every chart and table for readability. Can you tell which model each mark is without hovering? Does the legend match the marks? Do any labels overlap? Do the axes have units? Can a failure be mapped to its "pNN name (Lk)" problem? Do the counts agree with the text next to the chart? Use key "chart:...".` },
]

const seen = new Set()
const log2 = []
let clean = 0
for (let round = 1; round <= MAX && clean < 2; round++) {
  phase('Check')
  const found = (await parallel(LENSES.map(L => () => agent(`${L.p}\n${COMMON}\nRound ${round}.`,
    { label: `r${round}:${L.k}`, phase: 'Check', schema: FINDINGS, agentType: 'reviewer' }))))
    .filter(Boolean).flatMap(r => r.findings).filter(f => f.severity !== 'polish')
  const fresh = found.filter(f => !seen.has(f.key))
  fresh.forEach(f => seen.add(f.key))
  log(`round ${round}: ${found.length} open, ${fresh.length} new`)
  log2.push({ round, open: found.length, fresh: fresh.length })
  if (!found.length) { clean++; continue }
  clean = 0
  phase('Fix')
  const fix = await agent(
    `Steer Codex to fix these report-page findings in ${REPO}; you guide and verify, you do not write the fixes.\nFindings (JSON):\n${JSON.stringify(found)}\n
Write a numbered brief to ${OUT}/brief-r${round}.md. Run \`cd ${REPO} && codex exec -m gpt-6.1-sol -c model_reasoning_effort=high -c service_tier=priority -s workspace-write --skip-git-repo-check --json - < brief\`; later turns use \`codex exec resume <thread> -c sandbox_mode=workspace-write ... --json - < nudge\`. At most ${TURNS} turns.
Codex must not call models or touch results/*.jsonl or cache/. After each turn: \`make report\`, \`python3 -m analysis.audit\` (must print OK), \`python3 -m pytest -q tests\`.
Then commit yourself with the trailers "Co-authored-by: Chimera <<operator-email>>" and "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
Return: the commit hash, each finding as fixed/partial/not fixed, and one line on how Codex behaved.`,
    { label: `r${round}:fix`, phase: 'Fix', agentType: 'builder' })
  log2.push({ round, fix })
}
return { converged: clean >= 1, rounds: log2 }
