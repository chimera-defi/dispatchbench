<header class="head">
<span class="eyebrow">Run 2026-10-22b · {{n_problems}} problems × {{repeats}} attempts = {{n_calls}} calls per config · {{claude_usd}} Claude, {{codex_usd}} Codex (proxy), main + repo runs</span>
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a></nav>
</header>
<section class="verdict" id="winner">
<span class="eyebrow"><span class="num"></span>🏆 WINNER</span>
<ol class="recs">
<li><b>Codex has quota? sol61-high.</b> Haiku repairs only if a check fails. {{claude_zero}} on the Claude bill.</li>
<li>Codex out? haiku-low; haiku-high if a miss is costly: never missed, {{hh_upp}} per pass.</li>
<li>Need it faster? astra-medium: also never missed, about {{x_astra_vs_s61h}} the Codex usage.</li>
</ol>
<ul class="tight">
<li>✅ haiku-medium: {{haiku_medium_k}} on all problems, 0 misses on the hard set (its {{rescue_n}} main-run attempts on those problems, not a new run). {{haiku_medium_upp}} per pass, {{haiku_medium_med}}s. Measured $, not estimated.</li>
<li>💸 haiku-low: {{haiku_low_k}} at {{haiku_low_upp}}. Misses: too slow or a crash, never a wrong answer.</li>
<li>🛡️ Never missed (main set, hardest rung, all {{ag_n}} repo tasks): sol61-high {{x_sol61_high_med}}s and astra-medium {{x_astra_medium_med}}s median, both billed to Codex. sonnet-medium never missed either ({{sm_all}}), at {{sm_vs_hm_x}} haiku-medium's cost.</li>
<li>🐢 The Codex picks are slow on repo tasks: {{ag_sol61_high_med}}s and {{ag_astra_medium_med}}s median against about {{ag_claude_med}}s for a Claude builder.</li>
<li>🎯 Parity starts at haiku-high: {{hh_k}}, {{hh_hk}} on L7, {{ag_hh_k}} repo tasks. {{hh_upp}} per pass, {{hh_med}}s median: {{hh_s61h_x}} cheaper than sol61-high, {{hh_astra_x}} cheaper than astra-medium, and faster than both. haiku-medium missed {{hm_l7_miss}} on L7 ({{hm_l7_k}}).</li>
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
<li>Pass = every hidden test passes (fixed, random vs the reference solution, large for speed).</li>
<li>Sample tests = the worked examples in the problem text. Cheap to run, and the model can see them.</li>
<li>Claude $ from the CLI. Codex $ = tokens × list price (marked ~). Intervals: bootstrap, {{n_boot}} resamples.</li>
<li>Run by a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
</ul>
<details><summary>Exact commands</summary>
<ul class="tight small cmds">
{{w_flags}}
<li>luna-low-bare and luna-high-bare add the stripped harness from bench/trim_probe.py. Every luna-high row on the hard set uses it.</li>
</ul>
</details>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="dot hollow" style="color:var(--codex)"></span>exploratory</span><span><span class="ring"></span>Pareto frontier</span><span>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet · ▲ luna · ◆ sol · ★ astra.</span><span>Only frontier points are labelled; hover, tap or focus a point or a key row for the rest.</span></div>
<div class="tabs"><input type="radio" name="pset" id="pset-all" checked><label for="pset-all">All problems</label><input type="radio" name="pset" id="pset-hard"><label for="pset-hard">Hard set + pipelines</label>
<div class="tab tab-all">
<div class="chart">{{w_pass_cost}}</div>
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate. Whiskers: 95% CI.</li>
<li>Dashed hollow = Codex pilot, default → ⚡ fast mode, on {{fast_problems}} easier well-known LeetCode problems (every call passed). Not comparable, never on the frontier.</li>
<li>luna-low and luna-medium are cheapest here but pass only {{luna_low_pass}} and {{luna_medium_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}. Dashed hollow = Codex pilot, default → ⚡ fast mode, on {{fast_problems}} well-known LeetCode problems; not on the frontier.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_front_speed}}.</li>
<li>Pipelines ran only on the hard set: see the "Hard set + pipelines" tab.</li>
</ul>
</div>
<div class="tab tab-hard">
<div class="chart"><h3>Hard set: pass rate vs $ per pass</h3><p class="sub">{{rescue_n}} attempts on {{r_pids}} problems chosen after round 1 (luna-low fails them most). Single models: their main-run attempts. Purple = pipelines: low / high-bare is the luna build; plan→ = Haiku plans, luna builds; →H fail = Haiku fixes only when sample tests fail; →retry = luna tries again; →H all = Haiku fixes every answer. sol61-high and astra-medium →H fail sit on their own dots: the check never failed. Small sample, no intervals.</p>{{w_hard_pass_cost}}</div>
<ul class="tight small">
<li>Best trade-offs, cheapest first: {{w_hard_front_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Hard set: speed vs $ per pass</h3><p class="sub">Best trade-offs among rows passing at least {{min_pass}}. sol61-high and astra-medium →H fail: the check never failed, so these are separate runs of the model alone; their times differ by run.</p>{{w_hard_speed_cost}}</div>
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
<li>haiku-low: {{hl_timeouts}} too slow, {{hl_crashes}} crash, 0 wrong outputs in {{hl_attempts}} tries.</li>
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
<li><b>★ pick</b>: the recommendation. <b>budget pick</b>: cheapest config passing 95% or more.</li>
<li><b>0 misses</b>: every attempt passed. <b>0 misses, cheapest</b>: the cheapest such hard-set row. <b>missed N</b>: N attempts failed.</li>
<li><b>beaten</b>: something else is as cheap and passes as often. <b>pricier, passes more</b>: a real trade-off.</li>
<li><b>avoid</b>: passes under {{min_pass}}.</li>
</ul>
</details>
<details><summary>Full table with intervals</summary>
{{table:result}}
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per call</h3><p class="sub">Pilot, {{fast_problems}} well-known LeetCode problems × {{fast_rounds}} rounds; every call passed. The main run used the default tier.</p>{{w_fast}}</div>
<ul class="tight small">
<li>Fast-mode $ = list price × {{fast_mult}}, the multiplier on the pricing page; not a measured bill. sol61-low got faster ({{fast_sol_def}}s → {{fast_sol_fast}}s); luna-low did not ({{fast_luna_def}}s → {{fast_luna_fast}}s).</li>
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
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<div class="chart floor"><h3>Hard set: passes, $ per pass, median seconds</h3><p class="sub">{{rescue_n}} attempts on {{r_pids}} problems chosen after round 1 (luna-low fails them most). Single models: their main-run attempts. Purple = pipelines. plan→ = Haiku plans, luna builds. →H fail = Haiku fixes only when sample tests fail. →retry = luna tries again. →H all = Haiku fixes every answer.</p>{{w_pipes}}</div>
<ul class="tight small">
<li>✅ Haiku fixing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}. But haiku-medium alone also had 0 misses, {{hm_vs_pipe_x}} cheaper.</li>
<li>⚠️ Sample tests are a weak gate: they caught {{g_hi_fixed}} bad luna-high answers and missed {{g_hi_missed}}. luna-low fails them more often ({{g_lo_fixed}} repairs), so the gate helps it more.</li>
<li>✅ sol61-high and astra-medium → Haiku if samples fail: {{r_sol61_high_haiku_on_fail_k}} and {{r_astra_medium_haiku_on_fail_k}}. The gate never fired ({{g_sol61_repairs}} and {{g_astra_repairs}} repairs): they passed alone.</li>
<li>❌ A Haiku plan before luna helped less: luna-low {{r_haiku_low_plan_luna_low_k}}, luna-high {{r_haiku_low_plan_luna_high_bare_k}} (alone: {{r_luna_high_bare_k}}). Check after, don't plan first.</li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<span class="eyebrow"><span class="num"></span>✅ CONCLUSION</span>
<b>Delegate only to a model you can trust.</b>
<ol class="recs">
<li>Codex has quota: sol61-high, haiku-low repairs only on a failed check ({{claude_zero}} Claude).</li>
<li>Faster, more Codex usage: astra-medium, same repair.</li>
<li>Claude only (Codex out): haiku-low (<code>claude -p --tools ""</code>); haiku-high on a failed check or when a miss is costly.</li>
<li>Zero misses on the Claude side: sonnet-medium.</li>
<li>Best luna + Haiku pipeline: also 0 misses, but {{hm_vs_pipe_x}} the cost of haiku-medium alone.</li>
<li>Never luna-low or luna-medium alone.</li>
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
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
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
<details><summary>⚡ Codex fast mode and xhigh</summary>
{{table:fastmode}}
<ul class="tight">
<li>Fast mode: same passes and code, {{fm_fast_s}} s vs {{fm_ctrl_s}} s per call ({{fm_faster}} faster), {{fm_mult}} price.</li>
<li>xhigh: same passes, {{fm_x_cost}} the cost, slower, no better code.</li>
<li>Blind read, {{bl_n}} solutions: all {{bl_blocks}} blocks were sonnet-medium.</li>
</ul>
{{table:blind}}
</details>
<details><summary>📎 Appendix</summary>
<ul class="tight">
<li>Harder L7 rung: haiku-low {{l7_haiku_low_upp}} per pass, sonnet-medium {{l7_sonnet_medium_upp}}.</li>
<li>Escalation: luna-high passed {{esc_k}} where {{esc_vs}} passed {{esc_base}}.</li>
<li>When sample tests fail, Haiku fixes vs luna-high retries: {{r_luna_high_bare_haiku_on_fail_k}} at {{r_luna_high_bare_haiku_on_fail_upp}} vs {{r_luna_high_bare_retry_on_fail_k}} at {{r_luna_high_bare_retry_on_fail_upp}}.</li>
<li>Pilot ({{pilot_problems}} well-known LeetCode problems): every config passed, so it ranked nothing.</li>
<li>Original luna-low → Haiku fixes all run passed {{r_luna_low_haiku_low_repair_k}}; its prompt was not kept. Rerun from committed code: {{r_luna_low_haiku_review_all_k}}.</li>
<li>Repo tasks ({{n_tasks}} × {{agent_repeats}}, with tools): every config passed {{ag_k}}. $ per run: luna-low {{ag_luna_low_usd}}, haiku-low {{ag_haiku_low_usd}}, sonnet-medium {{ag_sonnet_medium_usd}}, sol61-medium {{ag_sol61_medium_usd}}.</li>
</ul>
</details>
</section>
