<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a></nav>
</header>
<section class="verdict" id="winner">
<span class="eyebrow"><span class="num"></span>🏆 WINNER</span>
<ol class="recs">
<li><b>Codex has quota? sol61-high (default tier).</b> Haiku repairs only if a check fails; it never fired. {{claude_zero}} on the Claude bill. In fast mode (⚡) the same pipeline runs {{ff_s61_faster}} quicker at {{ff_s61_x}} the Codex price, same {{ff_s61_k}}.</li>
<li>Codex out? haiku-low ({{haiku_low_upp}} per pass, {{haiku_low_k}}); haiku-high when a miss is costly (never missed, {{hh_upp}} per pass).</li>
<li>Need it faster? astra-medium: also never missed on the main ladder and L7 set, about {{x_astra_vs_s61h}} the Codex usage.</li>
</ol>
<ul class="tight">
<li>✅ haiku-medium: {{haiku_medium_k}} on the main ladder, 0 misses on the rescue set (its {{rescue_n}} main-run attempts on those problems, not a new run). {{haiku_medium_upp}} per pass, {{haiku_medium_med}}s. Measured $, not estimated.</li>
<li>💸 haiku-low: {{haiku_low_k}} on the main ladder at {{haiku_low_upp}}. Misses: too slow or a crash, never a wrong answer.</li>
<li>🛡️ Never missed on the main ladder, the L7 set and all {{ag_n}} repo-task runs ({{n_tasks}} tasks × {{agent_repeats}}): sol61-high {{x_sol61_high_med}}s and astra-medium {{x_astra_medium_med}}s median, both billed to Codex; sonnet-medium ({{sm_all}} + {{ag_sm_k}}), at {{sm_vs_hm_x}} haiku-medium's cost.</li>
<li>🐢 The Codex picks are slow on repo tasks: {{ag_sol61_high_med}}s and {{ag_astra_medium_med}}s median against about {{ag_claude_med}}s for a Claude builder.</li>
<li>🎯 Parity starts at haiku-high: {{hh_k}}, {{hh_hk}} on the L7 set, {{ag_hh_k}} repo tasks. {{hh_upp}} per pass, {{hh_med}}s median: {{hh_s61h_x}} cheaper than sol61-high, {{hh_astra_x}} cheaper than astra-medium, and faster than both. haiku-medium missed {{hm_l7_miss}} on the L7 set ({{hm_l7_k}}).</li>
<li>⚡ Fast mode (Codex priority tier, same model and effort) changed speed and price, not passes. sol61-high ⚡: {{ff_s61_k}} on the main ladder, {{ff_s61_hk}} on the L7 set, {{ff_s61_upp}} per pass and {{ff_s61_med}}s against {{ff_s61_dupp}} and {{ff_s61_dmed}}s at the default tier ({{ff_s61_faster}} quicker, {{ff_s61_x}} the price). astra-medium ⚡: {{ff_ast_k}} and {{ff_ast_hk}}, {{ff_ast_upp}} and {{ff_ast_med}}s against {{ff_ast_dupp}} and {{ff_ast_dmed}}s ({{ff_ast_faster}} quicker, {{ff_ast_x}} the price).</li>
</ul>
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Run 2026-10-22b · {{n_problems}} problems × {{repeats}} attempts = {{n_calls}} calls per config · {{claude_usd}} Claude, {{codex_usd}} Codex (estimated from tokens, not billed), all runs.</p>
<details><summary>📚 Problems by set (Easy/Medium/Hard)</summary>
<p class="small">The LeetCode links are the closest analogues I found by hand, not where the problems came from: the problems were written for this bench. The Easy/Medium/Hard badge is a guess at the LeetCode difficulty; the rung (L1 to L7) is this bench's own order. They need not agree: {{badge_disagreements}}.</p>
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
<ul class="tight small cmds">
{{w_flags}}
<li>luna-low-bare and luna-high-bare add the stripped harness (the Codex CLI’s own system prompt and tool text, trimmed by bench/trim_probe.py). Every luna-high row on the rescue set uses it.</li>
</ul>
</details>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
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
<li>Pipelines ran only on the rescue set: see the "Rescue set + pipelines" tab.</li>
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
<p class="small">Scroll sideways for more configs. E/M/H = my LeetCode difficulty guess.</p>
{{w_grid}}
<ul class="tight small">
<li>{{worst_failure}}; p04 taller_within sinks luna low and medium.</li>
<li>haiku-low: main ladder — {{hl_main_failures}}; L7 set — {{hl_l7_failures}}.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
{{w_short_table}}
<ul class="tight small">
<li>Click a header to sort. ~ = Codex $ estimated from token prices. → = a second step after the first. Claude $ = the part billed to the Claude CLI; Codex calls bill Codex. ≥N% (all passed) = lower {{ci_level}} bound when nothing failed.</li>
</ul>
<details class="small"><summary>What the verdicts mean</summary>
<ul class="tight small">
<li><b>★</b>: the routing pick in Winner. <b>budget pick</b>: cheapest config passing 95% or more.</li>
<li><b>0 misses</b>: every attempt passed. <b>0 misses, cheapest</b>: the cheapest such rescue-set row. <b>missed N</b>: N attempts failed.</li>
<li><b>beaten</b>: something else is as cheap and passes as often. <b>pricier, passes more</b>: a real trade-off.</li>
<li><b>avoid</b>: passes under {{min_pass}}.</li>
</ul>
</details>
<details><summary>Full table with intervals</summary>
{{table:result}}
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3><p class="sub">Default → ⚡ pairs for sol61-high and astra-medium on the main ladder and L7 set. Same model and effort; default and priority service tiers. All passed.</p>{{w_fast}}</div>
<ul class="tight small">
<li>Fast-mode $ uses {{fm_mult}} the list price (the pricing-page multiplier, not a measured bill).</li>
</ul>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Stripping the Codex harness (the CLI’s own system prompt and tool text) cuts luna’s input {{in_cut}}. Still more than haiku-low's {{haiku_low_in}} tokens per call.</li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<div class="chart floor"><h3>Rescue set: passes, $ per pass, median seconds</h3><p class="sub">Rescue set: see the sets box in Cost vs accuracy. {{w_decoder}} The ⚡ →H fail rows are derived: check never failed.</p>{{w_pipes}}</div>
<ul class="tight small">
<li>✅ Haiku fixing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}. But haiku-medium alone also had 0 misses, {{hm_vs_pipe_x}} cheaper.</li>
<li>⚠️ In a fresh luna-high-bare run the sample tests fired on {{g_hi_fixed}} of {{g_hi_bad}} bad answers (Haiku fixed them) and let {{g_hi_missed}} through; the ungated run had {{r_luna_high_bare_miss}} misses.</li>
<li>✅ sol61-high and astra-medium → Haiku if samples fail: {{r_sol61_high_haiku_on_fail_k}} and {{r_astra_medium_haiku_on_fail_k}}; the check never failed ({{g_sol61_repairs}} and {{g_astra_repairs}} repairs). In fast mode the check also never failed on any of the {{pf_s61_n_all}} sol61-high ⚡ answers (main ladder + L7 set), so the ⚡ pipeline is sol61-high ⚡ alone: main ladder {{pf_s61_k}}, {{pf_s61_upp}} per pass, {{pf_s61_med}} s vs {{pf_s61_dupp}}, {{pf_s61_dmed}} s at the default tier (quicker, about {{ff_s61_x}} the Codex list price, {{claude_zero}} Claude). For astra-medium ⚡ the check never failed on {{pf_ast_n_all}} answers (main ladder + L7 set): main ladder {{pf_ast_k}}, {{pf_ast_upp}} per pass, {{pf_ast_med}} s vs {{pf_ast_dupp}}, {{pf_ast_dmed}} s at the default tier ({{ff_ast_faster}} quicker, {{ff_ast_x}} the Codex list price, {{claude_zero}} Claude). Derived from cached answers, not separate runs.</li>
<li>❌ A Haiku plan before luna helped luna-low ({{r_luna_low_k}} → {{r_haiku_low_plan_luna_low_k}}) but not luna-high-bare ({{r_luna_high_bare_k}} either way), and both cost more than Haiku checking after.</li>
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
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run}}
</details>
</section>
<section class="notes">
<details><summary>⚠️ Caveats</summary>
<ul class="tight">
<li>Small sample: read the intervals before the point estimates.</li>
<li>{{n_exploratory}} configs were added after the main run: {{exploratory_names}}, including the Winner’s sol61-high and astra-medium.</li>
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
<li>Latency is CLI wall clock, up to {{lanes}} calls in flight on one host.</li>
<li>One run in time; hosted models change.</li>
</ul>
</details>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
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
<li>Main-ladder/L7 set fast runs: sol61-high ⚡ {{ff_s61_k}} / {{ff_s61_hk}}, {{ff_s61_upp}} per pass, {{ff_s61_med}} s; astra-medium ⚡ {{ff_ast_k}} / {{ff_ast_hk}}, {{ff_ast_upp}}, {{ff_ast_med}} s. Their derived →H fail pipelines equal the builders: {{pf_s61_fails}} / {{pf_ast_fails}} sample-test failures.</li>
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
