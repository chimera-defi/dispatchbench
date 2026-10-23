<header class="head">
<span class="eyebrow">Run 2026-10-22b · {{n_problems}} problems × {{repeats}} attempts = {{n_calls}} calls per config · {{claude_usd}} Claude, {{codex_usd}} Codex (proxy)</span>
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a></nav>
</header>
<section class="verdict" id="winner">
<span class="eyebrow"><span class="num"></span>🏆 WINNER</span>
<ol class="recs">
<li><b>Build with luna-high.</b></li>
<li><b>Have haiku-low check every answer.</b></li>
<li>In a hurry? Build with luna-low; call Haiku only if the sample tests fail.</li>
</ol>
<ul class="tight">
<li>✅ Build + check never failed on the hard set ({{r_luna_high_bare_haiku_review_all_k}}), {{g_vs_sm_x}} cheaper than sonnet-medium. Slower: {{r_luna_high_bare_haiku_review_all_s}} per answer vs {{r_sonnet_medium_s}}.</li>
<li>⚡ Fast option: {{r_luna_low_haiku_on_fail_k}} in {{r_luna_low_haiku_on_fail_s}}, the fastest.</li>
<li>One model only? haiku-low: {{haiku_low_pass}} at {{haiku_low_upp}} per pass.</li>
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
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>Pass = every hidden test passes (fixed, random vs brute force, large for speed).</li>
<li>Sample tests = the worked examples in the problem text. Cheap to run, and the model can see them.</li>
<li>Claude $ from the CLI. Codex $ = tokens × list price (marked ~). Intervals: bootstrap, {{n_boot}} resamples.</li>
<li>Run by a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
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
<div class="tabs"><input type="radio" name="pset" id="pset-all" checked><label for="pset-all">All problems</label><input type="radio" name="pset" id="pset-hard"><label for="pset-hard">Hard set + pipelines</label>
<div class="tab tab-all">
<div class="chart">{{w_pass_cost}}</div>
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate. Whiskers: 95% CI.</li>
<li>luna-low and luna-medium are cheapest but pass only {{luna_low_pass}} and {{luna_medium_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: haiku-low and luna-high.</li>
<li>Codex fast mode is not plotted: it only ran on {{fast_problems}} easy problems where every call passed. See Results.</li>
</ul>
</div>
<div class="tab tab-hard">
<div class="chart"><h3>Hard set: pass rate vs $ per pass</h3><p class="sub">{{rescue_n}} attempts on the problems luna-low failed most. Purple = pipelines: low/high is luna's effort; →H all = Haiku checks every answer; →H fail = Haiku only when sample tests fail. Small sample, no intervals.</p>{{w_hard_pass_cost}}</div>
<ul class="tight small">
<li>Best trade-offs, cheapest first: {{w_hard_front_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Hard set: speed vs $ per pass</h3><p class="sub">Best trade-offs among rows passing at least {{min_pass}}.</p>{{w_hard_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_hard_front_speed}}.</li>
</ul>
</div>
</div>
</section>
<section id="fail">
<h2><span class="num"></span>🟥 Where they fail</h2>
{{w_grid}}
<ul class="tight small">
<li>p12 crashes most configs; p04 sinks luna low and medium.</li>
<li>haiku-low never gave a wrong answer: its misses are {{hl_timeouts}} timeouts and {{hl_crashes}} crash in {{hl_attempts}} tries.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
{{w_short_table}}
<ul class="tight small">
<li>Click a header to sort. ~ = Codex $ estimated from token prices. → = a second step after the first.</li>
</ul>
<details class="small"><summary>What the verdicts mean</summary>
<ul class="tight small">
<li><b>★ best</b>: cheapest hard-set row that never failed.</li>
<li><b>checker</b> / <b>builder</b>: the picks in the recommendation (both pass at least {{min_pass}}).</li>
<li><b>never failed</b>: every attempt passed. <b>missed N</b>: N attempts failed.</li>
<li><b>beaten</b>: something else is as cheap and passes as often. <b>pricier, passes more</b>: a real trade-off.</li>
<li><b>avoid</b>: passes under {{min_pass}}.</li>
</ul>
</details>
<details><summary>Full table with intervals</summary>
{{table:result}}
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per call</h3><p class="sub">Pilot, {{fast_problems}} easy problems × {{fast_rounds}} rounds; every call passed. The main run used the default tier.</p>{{w_fast}}</div>
<ul class="tight small">
<li>Fast mode costs {{fast_mult}}×. sol61-low got faster ({{fast_sol_def}}s → {{fast_sol_fast}}s); luna-low did not ({{fast_luna_def}}s → {{fast_luna_fast}}s).</li>
</ul>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Stripping the Codex harness cuts luna's input {{in_cut}}. Still more than Claude's {{haiku_low_in}}.</li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: Haiku checks luna's work</h2>
<div class="chart floor"><h3>Hard set: passes, $ per pass, median seconds</h3><p class="sub">{{rescue_n}} attempts on the problems luna-low failed most. Purple = luna builds, then Haiku checks: H all = every answer; H fail = only when sample tests fail.</p>{{w_pipes}}</div>
<ul class="tight small">
<li>✅ Haiku checks every luna-high answer: {{r_luna_high_bare_haiku_review_all_k}}, {{g_vs_sm_x}} cheaper than sonnet-medium.</li>
<li>⚠️ Sample tests are a weak gate: they caught {{g_hi_fixed}} bad luna-high answers and missed {{g_hi_missed}}. luna-low fails them more often ({{g_lo_fixed}} repairs), so the gate helps it more.</li>
<li>❌ A Haiku plan before luna helped less: luna-low {{r_haiku_low_plan_luna_low_k}}, luna-high {{r_haiku_low_plan_luna_high_bare_k}} (alone: {{r_luna_high_bare_k}}). Check after, don't plan first.</li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<span class="eyebrow"><span class="num"></span>✅ CONCLUSION</span>
<b>No single model wins: route by risk.</b>
<ol class="recs">
<li>Build: luna-high.</li>
<li>Check: haiku-low on every answer (<code>claude -p --tools ""</code>).</li>
<li>Speed first: luna-low, Haiku only if sample tests fail.</li>
<li>Zero misses allowed, no checker: sonnet-medium.</li>
<li>Never luna-low or luna-medium without a Haiku check.</li>
</ol>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<details><summary>🎛️ Explorer and more charts</summary>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:heatmap.svg|Pass rate per problem and config}}
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:cost_time.svg|Cost vs time per pass}}
{{chart:token_in.svg|Input tokens per call}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run}}
</details>
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
<li>When sample tests fail, Haiku fixes vs luna-high retries: {{r_luna_high_bare_haiku_on_fail_k}} at {{r_luna_high_bare_haiku_on_fail_upp}} vs {{r_luna_high_bare_retry_on_fail_k}} at {{r_luna_high_bare_retry_on_fail_upp}}.</li>
<li>Pilot ({{pilot_problems}} easy problems): every config passed, so it ranked nothing.</li>
<li>Original luna-low → Haiku checks all run passed {{r_luna_low_haiku_low_repair_k}}; its prompt was not kept. Rerun from committed code: {{r_luna_low_haiku_review_all_k}}.</li>
<li>Repo tasks ({{n_tasks}} × {{agent_repeats}}, with tools): every config passed {{ag_k}}. $ per run: luna-low {{ag_luna_low_usd}}, haiku-low {{ag_haiku_low_usd}}, sonnet-medium {{ag_sonnet_medium_usd}}, sol61-medium {{ag_sol61_medium_usd}}.</li>
</ul>
</details>
</section>
