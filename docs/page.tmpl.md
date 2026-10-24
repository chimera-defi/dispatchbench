<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p class="small">Test sets: main ladder {{n_problems}}×{{repeats}}={{n_calls}}; L7 {{n_l7}}×{{repeats}}={{l7_n}}; rescue {{n_rescue_problems}}×{{repeats}}={{rescue_n}}; repo tasks {{n_tasks}}×{{agent_repeats}}={{ag_n}}.</p>
<ol class="recs">
<li><b>Codex has quota? sol61-high (default tier).</b> The check runs the problem’s worked examples; Haiku repairs only if they fail. No repairs fired. {{claude_zero}} on the Claude bill.</li>
<li>Codex out? haiku-low ({{haiku_low_upp}} per pass, {{haiku_low_k}}); haiku-high when a miss is costly (never missed, {{hh_upp}} per pass).</li>
<li>Need it faster? haiku-high: {{hh_med}} s, never missed, {{hh_upp}} per pass on the Claude bill. Must stay on Codex? astra-medium: {{x_astra_medium_med}} s; Codex cost about {{x_astra_vs_s61h}} vs sol61-high.</li>
</ol>
<ul class="tight">
<li>✅ haiku-medium: {{haiku_medium_k}} on the main ladder, 0 misses on the rescue set (its {{rescue_n}} main-run attempts on those problems, not a new run). {{haiku_medium_upp}} per pass, {{haiku_medium_med}}s. Measured $, not estimated.</li>
<li>💸 haiku-low: {{haiku_low_k}} on the main ladder at {{haiku_low_upp}}. Misses: too slow or a crash, never a wrong answer.</li>
<li>🛡️ sol61-high and astra-medium never missed on the main ladder, L7 or repo tasks: {{x_sol61_high_med}}s and {{x_astra_medium_med}}s main-ladder medians, both billed to Codex.</li>
<li>🛡️ sonnet-medium also never missed: {{sm_all}} main ladder + L7, {{ag_sm_k}} repo tasks, at {{sm_vs_hm_x}} haiku-medium's main-ladder cost.</li>
<li>🐢 The Codex picks are slow on repo tasks: {{ag_sol61_high_med}}s and {{ag_astra_medium_med}}s median against about {{ag_claude_med}}s for a Claude builder.</li>
<li>🎯 haiku-high is the cheapest config with no misses across these sets: {{hh_k}}, {{hh_hk}} on the L7 set, {{ag_hh_k}} repo tasks. {{hh_upp}} per pass, {{hh_med}}s median: {{hh_s61h_x}} cheaper than sol61-high, {{hh_astra_x}} cheaper than astra-medium, and faster than both. haiku-medium missed {{hm_l7_miss}} on the L7 set ({{hm_l7_k}}).</li>
<li>⚡ Faster sol61-high: fast mode ({{ff_s61_med}} s). astra-medium fast ({{ff_ast_med}} s) is fastest among main-ladder configs with no misses; pairs are in Results.</li>
</ul>
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Every config faced the same new problems and hidden tests, with tools off. {{n_problems}} problems × {{repeats}} attempts = {{n_calls}} calls per config; total spend: {{claude_usd}} Claude, {{codex_usd}} Codex (estimated from tokens).</p>
<details><summary>📚 Problems by set (Easy/Medium/Hard)</summary>
<p class="small">Outside the pilot, LeetCode links are the closest analogues I found by hand; the problems were written for this bench. Pilot links are labelled source because those problems came from LeetCode. The Easy/Medium/Hard badge is a guess at the LeetCode difficulty; the rung (L1 to L7) is this bench's own order. They need not agree: {{badge_disagreements}}.</p>
<ul class="tight small">
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>Pass = every hidden test passes: the fixed cases, random cases checked against the reference solution, and large cases for speed.</li>
<li>Sample tests = the worked examples in the problem text. Cheap to run, and the model can see them.</li>
<li>Claude $ from the CLI. Codex $ = tokens × list price; ~ means estimated from tokens, not billed. {{ci_level}} intervals from {{n_boot}} bootstrap resamples (how much the pass rate would wobble on a rerun).</li>
<li>Run by Wren, a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
</ul>
<details><summary>Exact commands</summary>
<p class="small">Run {{run_id}}.</p>
<ul class="tight small cmds">
{{w_flags}}
<li>luna-low-bare and luna-high-bare add the stripped harness (the Codex CLI’s own system prompt and tool text, trimmed by bench/trim_probe.py). Every luna-high row on the rescue set uses it.</li>
</ul>
</details>
<p class="small"><b>Did we test whether Claude's harness makes Codex look bad?</b> Codex ran in its own CLI with <code>--ignore-user-config</code> and tools off. The stripped-harness rows (<code>luna-*-bare</code>) are the sensitivity check. Codex-as-orchestrator run: {{codex_orchestrator_status}}.</p>
<p class="small">On repo tasks, host AGENTS.md instructions accounted for {{host_sol61_medium}} of {{shell_sol61_medium}} sol61-medium shell commands and {{host_luna_low}} of {{shell_luna_low}} luna-low commands (HOST_DOC count); Codex latency includes that overhead.</p>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<p class="small">Haiku is cheap and accurate; Codex’s strongest configs trade more usage for reliable passes. Compare each set separately.</p>
{{w_sets}}
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="ring"></span>Pareto frontier</span><span>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet · ▲ luna · ◆ sol · ★ astra. ⚡ = fast mode, joined to its default-tier twin.</span><span>Only frontier points are labelled; hover, tap or focus a point or a key row for the rest.</span></div>
<div class="tabs"><input type="radio" name="pset" id="pset-all" checked><label for="pset-all">Main ladder</label><input type="radio" name="pset" id="pset-hard"><label for="pset-hard">Rescue set + pipelines</label>
<div class="tab tab-all">
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate. Whiskers: {{ci_level}} confidence interval (bootstrap).</li>
<li>luna-low, luna-low-bare (same model, stripped Codex harness, see Token floor) and luna-medium are the cheapest points but pass only {{luna_low_pass}}, {{luna_low_bare_pass}} and {{luna_medium_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_front_speed}}.</li>
<li>Hollow pipeline points use the rescue set, not the full ladder; they do not enter the ladder frontier. See the "Rescue set + pipelines" tab for a comparison on the same set.</li>
</ul>
</div>
<div class="tab tab-hard">
<div class="chart"><h3>Rescue set: pass rate vs $ per pass</h3><p class="sub">Rescue set: see the sets box above. Purple = pipelines. {{w_decoder}} sol61-high and astra-medium →H fail: the check never failed. sol61-high ⚡ and astra-medium ⚡ →H fail are derived from cached answers: check never failed. Small sample, no intervals.</p>{{w_hard_pass_cost}}</div>
<ul class="tight small">
<li>Best trade-offs, cheapest first: {{w_hard_front_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Rescue set: speed vs $ per pass</h3><p class="sub">Best trade-offs among rows passing at least {{min_pass}}. Default-tier sol61-high and astra-medium →H fail are separate runs of the model alone: the check never failed. sol61-high ⚡ and astra-medium ⚡ →H fail are derived from their fast builders (check never failed).</p>{{w_hard_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_hard_front_speed}}.</li>
</ul>
</div>
</div>
</section>
<section id="fail">
<h2><span class="num"></span>🟥 Where they fail</h2>
<p class="small">{{worst_failure}}. Cells show passed/attempted: green = all passed, amber = more than half, red = half or fewer; dash = not run. Scroll sideways for more configs. E/M/H = my LeetCode difficulty guess.</p>
{{w_grid}}
<ul class="tight small">
<li>p04 taller_within also sinks luna low and medium.</li>
<li>haiku-low: main ladder — {{hl_main_failures}}; L7 set — {{hl_l7_failures}}.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
<p class="small">sol61-high is the Codex routing pick; haiku-high is the cheapest config with no misses across the main ladder, L7 and repo tasks.</p>
{{w_short_table}}
<ul class="tight small">
<li>Click a header to sort. ~ = Codex $ estimated from token prices. → = a second step after the first. Claude $ = the part billed to the Claude CLI; Codex calls bill Codex. ≥N% (all passed) = lower {{ci_level}} bound when nothing failed.</li>
</ul>
<p class="small">Verdicts: ★ = Winner pick; budget pick = cheapest config passing {{budget_pass}} or more; <b>0 misses</b>: every attempt passed; “cheapest” compares those rows within the set. “one miss” or “missed N” counts failed attempts; beaten = another row is as cheap and passes as often; pricier, passes more = a trade-off; avoid = below {{min_pass}}.</p>
<details><summary>Full table with intervals and tail latency</summary>
{{table:result_detail}}
<p class="small">pass@1 is the fraction of individual attempts passing all hidden tests; p90 is the time within which {{p90_percent}} of calls finished; proxy means Codex cost estimated from tokens and list prices.</p>
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3><p class="sub">Default → ⚡ pairs for sol61-high and astra-medium on the main ladder and L7 set. Same model and effort; default and priority service tiers. All passed.</p>{{w_fast}}</div>
<ul class="tight small">
<li>Fast-mode $ uses {{fm_mult}} the list price (the pricing-page multiplier, not a measured bill).</li>
</ul>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<p class="small">Codex’s harness adds input before the task itself: this is the token floor. Bars show mean input per call, including the task, so they also capture prompt length.</p>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Stripping the Codex harness (the CLI’s own system prompt and tool text) cuts luna’s input {{in_cut}}. Still more than haiku-low's {{haiku_low_in}} tokens per call.</li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">Checking examples can catch some bad answers, but haiku-medium alone beat the best luna repair pipeline on cost with no rescue-set misses.</p>
<div class="chart floor"><h3>Rescue set: passes, $ per pass, median seconds</h3><p class="sub">Rescue set: see the sets box in Cost vs accuracy. {{w_decoder}} The ⚡ →H fail rows are derived: check never failed.</p>{{w_pipes}}</div>
<ul class="tight small">
<li>✅ Haiku fixing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}. But haiku-medium alone also had 0 misses, {{hm_vs_pipe_x}} cheaper.</li>
<li>⚠️ In a fresh luna-high-bare run the sample tests fired on {{g_hi_fixed}} of {{g_hi_bad}} bad answers (Haiku fixed them) and let {{g_hi_missed}} through; the ungated run had {{r_luna_high_bare_miss}} misses.</li>
<li>✅ sol61-high and astra-medium → Haiku if samples fail: {{r_sol61_high_haiku_on_fail_k}} and {{r_astra_medium_haiku_on_fail_k}}; no repairs fired. Fast-mode pipelines equal their builders because every example check passed (derived from cached answers).</li>
<li>❌ A Haiku plan before luna helped luna-low ({{r_luna_low_k}} → {{r_haiku_low_plan_luna_low_k}}) but not luna-high-bare ({{r_luna_high_bare_k}} either way), and both cost more than Haiku checking after.</li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>✅ CONCLUSION</h2>
<b>Use sol61-high for Codex quota; haiku-high for fast, reliable Claude runs.</b>
<ol class="recs">
<li>Codex has quota: sol61-high, haiku-low repairs only on a failed check ({{claude_zero}} Claude).</li>
<li>Need it faster? haiku-high: {{hh_med}} s, never missed, {{hh_upp}} per pass on the Claude bill. Must stay on Codex? astra-medium: {{x_astra_medium_med}} s; Codex cost about {{x_astra_vs_s61h}} vs sol61-high; same repair.</li>
<li>Claude only (Codex out): haiku-low (<code>claude -p --tools ""</code>); haiku-high on a failed check or when a miss is costly.</li>
<li>Zero misses on the Claude side: sonnet-medium.</li>
<li>Best luna + Haiku pipeline: luna-high-bare → Haiku reviews every answer; passed {{r_luna_high_bare_haiku_review_all_k}}, but cost {{hm_vs_pipe_x}} as much as haiku-medium alone.</li>
<li>Never luna-low or luna-medium alone.</li>
</ol>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<details><summary>🎛️ Explorer and more charts</summary>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run}}
</details>
</section>
<section class="notes">
<details><summary>⚠️ Caveats</summary>
<ul class="tight">
<li>Small sample: read the intervals before the point estimates.</li>
<li>Exploratory means added after seeing the main-run results, outside the original comparison. {{n_exploratory}} configs were added: {{exploratory_names}}, including the Winner’s sol61-high and astra-medium.</li>
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
<li>Latency is CLI wall clock, up to {{lanes}} calls in flight on one host.</li>
<li>One run in time; hosted models change.</li>
</ul>
</details>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
<p class="small">Fast-mode runs not scored here; see fast-mode table.</p>
<p class="small">Complexity = max cyclomatic complexity per function (radon); lint = ruff warnings; worse growth = time-growth exponent more than {{growth_margin}} above the reference’s.</p>
<ul class="tight">
<li>Main-ladder passing solutions only ({{q_rows}} rows); all {{n_solutions}} solutions are under results/solutions.</li>
<li>On {{q_worst_problem}}, {{q_slow_n}} solutions run {{q_slow_lo}} to {{q_worst_x}} slower than the reference across {{q_slow_cfgs}} configs; the largest is one {{q_worst_cfg}} solution.</li>
</ul>
</details>
<details><summary>⚡ Codex fast mode and xhigh</summary>
<p class="small">{{fm_n}} attempts = rescue set ({{r_pids}}) × {{repeats}}. The control is a separate default-tier run of sol61-high (repeats {{fm_rep_lo}}–{{fm_rep_hi}}), so its {{fm_ctrl_s}} s differs from the Results table’s rescue-set sol61-high row (repeats {{repeat_lo}}–{{repeats}}).</p>
{{table:fastmode}}
<ul class="tight">
<li>Fast mode: same passes and code, {{fm_fast_s}} s vs {{fm_ctrl_s}} s per call ({{fm_faster}} faster), {{fm_mult}} the list price (the pricing-page multiplier, not a measured bill).</li>
<li>xhigh: same passes, {{fm_x_cost}} the cost, slower, no better code.</li>
<li>Blind read, {{bl_n}} solutions: all {{bl_blocks}} blocks were sonnet-medium.</li>
</ul>
<p class="small">{{blind_caption}}</p>
{{table:blind}}
</details>
<details><summary>📎 Appendix</summary>
<ul class="tight">
<li>L7 set (p13–p15 × {{repeats}}): haiku-low {{l7_hl_k}} at {{l7_haiku_low_upp}} per pass, sonnet-medium {{l7_sm_k}} at {{l7_sonnet_medium_upp}}.</li>
<li>Escalation (retrying weak problems at higher effort): on {{esc_problems}}, luna-high passed {{esc_k}} where {{esc_vs}} passed {{esc_base}}.</li>
<li>Rescue set ({{rescue_n}} attempts): luna-high-bare→H fail vs luna-high-bare→retry: {{r_luna_high_bare_haiku_on_fail_k}} at {{r_luna_high_bare_haiku_on_fail_upp}} vs {{r_luna_high_bare_retry_on_fail_k}} at {{r_luna_high_bare_retry_on_fail_upp}}.</li>
<li>Pilot ({{pilot_problems}} well-known LeetCode problems): every config passed, so it ranked nothing. The fast-mode pilot ({{fast_problems}} problems × {{fast_rounds}} rounds) used {{fast_mult}} the list price: sol61-low got faster ({{fast_sol_def}}s → {{fast_sol_fast}}s), luna-low did not ({{fast_luna_def}}s → {{fast_luna_fast}}s); the only fast-mode data for low effort.</li>
<li>Rescue set ({{rescue_n}} attempts): original luna-low→H all run passed {{r_luna_low_haiku_low_repair_k}}; its prompt was not kept. Rerun from committed code: {{r_luna_low_haiku_review_all_k}}.</li>
<li>Repo tasks ({{n_tasks}} tasks × {{agent_repeats}} runs, with tools): every config passed {{ag_k}}. $ per run: luna-low {{ag_luna_low_usd}}, haiku-low {{ag_haiku_low_usd}}, sonnet-medium {{ag_sonnet_medium_usd}}, sol61-medium {{ag_sol61_medium_usd}}, haiku-high {{ag_haiku_high_usd}}, sol61-high {{ag_sol61_high_usd}}, astra-medium {{ag_astra_medium_usd}}.</li>
</ul>
</details>
</section>
