<header class="head">
<span class="eyebrow">Run 2026-10-22b · {{n_problems}} problems × {{repeats}} attempts = {{n_calls}} calls per config · {{claude_usd}} Claude, {{codex_usd}} Codex (proxy)</span>
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a></nav>
</header>
<section class="verdict" id="winner">
<span class="eyebrow"><span class="num"></span>🏆 WINNER</span>
<b>Build with luna-high, let haiku-low repair a failed check, and use sonnet-medium when no miss is acceptable.</b>
<ul class="tight">
<li>Cheapest safe single model: haiku-low, {{haiku_low_pass}} at {{haiku_low_upp}} per pass. luna-high: {{luna_high_pass}} at {{luna_high_upp}}.</li>
<li>A Haiku repair took luna-low from {{r_e_luna}} to {{r_luna_low_haiku_low_repair_k}} on its hardest problems. sonnet-medium passed {{sm_all}}.</li>
</ul>
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<details><summary>📚 Problems by round (Easy/Medium/Hard)</summary>
<ul class="tight small">
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>{{repeats}} attempts per problem per config, tools off. E/M/H: nearest LeetCode level, my estimate.</li>
<li>Pass = all hidden tests pass: fixed cases, random cases vs a brute force, big cases for speed.</li>
<li>Claude $ from the CLI; Codex $ = tokens × list price. Intervals: bootstrap, {{n_boot}} resamples.</li>
</ul>
<details><summary>Exact commands</summary>
<ul class="tight small cmds">
{{w_flags}}
<li>luna-low-bare adds the stripped harness from bench/trim_probe.py.</li>
</ul>
</details>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="dot hollow" style="color:var(--codex)"></span>exploratory</span><span><span class="ring"></span>Pareto frontier</span></div>
<div class="chart">{{w_pass_cost}}</div>
<ul class="tight small">
<li>Purple line: nothing beats these on both price and pass rate. Whiskers: 95% CI.</li>
<li>luna low and medium are cheapest but pass only {{luna_low_pass}} and {{luna_medium_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Frontier among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>haiku-low and luna-high: nothing as accurate is both faster and cheaper.</li>
</ul>
</section>
<section id="fail">
<h2><span class="num"></span>🟥 Where they fail</h2>
{{w_grid}}
<ul class="tight small">
<li>p12 crashes most configs; p04 sinks luna low and medium.</li>
<li>haiku-low never answers wrong: {{hl_timeouts}} timeouts and {{hl_crashes}} crash in {{hl_attempts}} tries.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
{{w_short_table}}
<ul class="tight small">
<li>Click a header to sort. ~ marks the Codex token-price proxy.</li>
</ul>
<details><summary>Full table with intervals</summary>
{{table:result}}
</details>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Stripping the Codex harness cuts luna's input {{in_cut}}; still above Claude's {{haiku_low_in}}.</li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: Haiku plans or checks luna's work</h2>
<div class="chart floor"><h3>Hard set: passes, $ per pass, median seconds</h3><p class="sub">The {{rescue_n}} attempts luna-low failed most. Purple: haiku-low plans before luna builds, or repairs after.</p>{{w_pipes}}</div>
<ul class="tight small">
<li>Only the repair pipeline and sonnet-medium passed every attempt; the repair pipeline cost under a quarter as much.</li>
<li>Haiku was {{r_e_haiku_share}} of the repair pipeline's cost. haiku-low alone is cheaper but missed {{r_e_more}}.</li>
<li>Repo tasks ({{n_tasks}} × {{agent_repeats}}, with tools): every config passed {{ag_k}}. $ per run: luna-low {{ag_luna_low_usd}}, haiku-low {{ag_haiku_low_usd}}, sonnet-medium {{ag_sonnet_medium_usd}}, sol61-medium {{ag_sol61_medium_usd}}.</li>
<li>A Haiku plan first lifted luna-low to {{r_haiku_low_plan_luna_low_k}} but left luna-high at {{r_haiku_low_plan_luna_high_bare_k}} (alone: {{r_luna_high_bare_k}}), at {{r_haiku_low_plan_luna_high_bare_upp}} vs {{r_luna_high_bare_upp}} per pass. Repair after beats plan first.</li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<span class="eyebrow"><span class="num"></span>✅ CONCLUSION</span>
<b>No single model wins: route by risk.</b>
<ol class="recs">
<li>Build: luna at high effort.</li>
<li>Failed check: haiku-low repairs, <code>claude -p --tools ""</code>.</li>
<li>No miss acceptable, or the hardest problems: sonnet-medium.</li>
<li>Never luna at low or medium effort, unless Haiku checks it.</li>
</ol>
<p class="small"><strong>💳 On a Codex plan:</strong> luna tokens are free until the quota resets, so luna-high first costs nothing; Claude is paid only when a check fails (luna-high passed {{r_luna_high_bare_k}} on the hard set). Derived from the prices, not a separate test.</p>
<p class="small muted">Why: luna-high is the cheapest config on the frontier, a Haiku repair closed every luna-low miss on the hard set ({{r_luna_low_haiku_low_repair_k}}), and only sonnet-medium never failed ({{sm_all}}).</p>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:heatmap.svg|Pass rate per problem and config}}
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:cost_time.svg|Cost vs time per pass}}
{{chart:token_in.svg|Input tokens per call}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run}}
</section>
<section class="notes">
<details><summary>⚠️ Caveats</summary>
<ul class="tight">
<li>Small sample: read the intervals before the point estimates.</li>
<li>luna-high was added after the main run (exploratory).</li>
<li>Codex cost swings up to {{cache_swing}} with prompt-cache hits.</li>
<li>Latency is CLI wall clock, up to {{lanes}} calls in flight on one host.</li>
<li>One run in time; hosted models change.</li>
</ul>
</details>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
<ul class="tight">
<li>Passing solutions only; all {{n_solutions}} are in the repo under results/solutions.</li>
<li>On {{q_worst_problem}}, {{q_slow_n}} solutions run {{q_slow_lo}} to {{q_worst_x}} slower than the reference.</li>
</ul>
</details>
<details><summary>📎 Appendix</summary>
<ul class="tight">
<li>Harder L7 rung: haiku-low {{l7_haiku_low_upp}} per pass, sonnet-medium {{l7_sonnet_medium_upp}}.</li>
<li>Escalation: luna-high passed {{esc_k}} where {{esc_vs}} passed {{esc_base}}.</li>
<li>Haiku repair of luna-low: {{r_luna_low_haiku_low_repair_k}} at {{r_luna_low_haiku_low_repair_upp}} per pass.</li>
<li>Pilot ({{pilot_problems}} easy problems): every config passed, so it ranked nothing.</li>
</ul>
</details>
</section>
