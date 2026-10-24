<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a><a href="#notes">Notes</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p><b>Use sol61-high when Codex has quota. Use haiku-low when it does not; use haiku-high when a miss would be costly or you need speed.</b></p>
<p class="small names">Names: haiku and sonnet are Claude; luna, sol and astra are Codex (OpenAI). Suffix = effort (low / medium / high). {{model_names}}.</p>
<ol class="recs">
<li>Codex has quota? sol61-high at normal speed (not fast mode). After it answers, run the problem's worked examples. If any fail, haiku-low fixes the answer. In this run no fix was ever needed. {{claude_zero}} on the Claude bill.</li>
<li>Codex out? haiku-low: passed {{haiku_low_passes}} of {{n_calls}}, {{haiku_low_upp}} per pass; haiku-high when a miss is costly: passed {{hh_passes}} of {{n_calls}}, {{hh_upp}} per pass.</li>
<li>Need speed? haiku-high: {{hh_med}} s, never missed, {{hh_upp}} per pass.</li>
</ol>
<p><b>Why:</b></p>
<ul class="tight small">
<li>haiku-high: never missed — {{hh_k}} main ladder, {{hh_hk}} L7, {{ag_hh_k}} repo tasks. {{hh_upp}} per pass, {{hh_med}} s. Measured $.</li>
</ul>
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Every config faced the same new problems and hidden tests, with tools off (the model could not run code, read files or search).</p>
<details><summary>📚 Problems by set (Easy/Medium/Hard)</summary>
<p class="small">Outside the pilot, LeetCode links are the closest analogues I found by hand; the problems were written for this bench. Pilot links are labelled source because those problems came from LeetCode. The Easy/Medium/Hard badge is a guess at the LeetCode difficulty; the rung (L1 to L7) is this bench's own order. They need not agree: {{badge_disagreements}}.</p>
<ul class="tight small">
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>The whole bench cost about {{claude_usd}} on Claude and an estimated {{codex_usd}} of Codex quota.</li>
<li>Sets: main ladder ({{n_problems}} problems × {{repeats}} = {{n_calls}}), L7 ({{n_l7}} × {{repeats}} = {{l7_n}}), rescue (the {{n_rescue_problems}} main-ladder problems that luna, Codex's cheap model, missed most × {{repeats}} = {{rescue_n}}), repo tasks ({{n_tasks}} edits with tools × {{agent_repeats}} = {{ag_n}}).</li>
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
<p class="small"><b>Q: Does Claude's harness make Codex look bad?</b><br><b>A: No bias of about {{hb_limit}} or more was detectable.</b> The confidence interval contains zero; this small subset is not proof of no bias.</p>
<p class="small">We had Codex build its own harness: the program that sends the problem to the model and grades the answer. We ran luna-low and haiku-low on both harnesses ({{hb_n_problems}} hard problems × {{hb_repeats}} repeats).</p>
<table><caption>Passed / attempted</caption><thead><tr><th>Model</th><th>Claude harness</th><th>Codex harness</th></tr></thead><tbody>
<tr><td>luna-low</td><td>{{hb_claude_luna_low}}</td><td>{{hb_codex_luna_low}}</td></tr>
<tr><td>haiku-low</td><td>{{hb_claude_haiku_low}}</td><td>{{hb_codex_haiku_low}}</td></tr>
</tbody></table>
<p class="small">The confidence interval is the range of bias the data support: {{hb_ci}}. Bias here means a change in the gap between the models' pass rates.</p>
<p class="small">The harnesses differ in mechanism: one-shot (answer once) vs tool loop (run code and revise), not just in who built them.</p>
<p class="small">Codex built and ran its harness with {{hb_errors}} harness errors and no timeouts, in about {{hb_minutes}} minutes of wall time for the recorded calls.</p>
<p class="small">In the main benchmark, Codex answered through its own command-line app, with personal settings ignored and tools off. We also tried luna with Codex's own system prompt and tool instructions removed (the <code>luna-*-bare</code> rows) to see how much those instructions affected the results.</p>
<p class="small">On repo tasks, instructions in the host's AGENTS.md file caused {{host_sol61_medium}} of {{shell_sol61_medium}} sol61-medium shell commands and {{host_luna_low}} of {{shell_luna_low}} luna-low commands. Those extra commands are included in Codex's measured time.</p>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<p class="small">Haiku is cheap and accurate; Codex’s strongest configs trade more usage for reliable passes.</p>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="ring"></span>Pareto frontier</span><span>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet · triangles luna (up = low, right = medium, down = high) · ◆ sol · ★ astra. Lighter blue = the {{older_generation}} generation; dashed edge = bare prompt. Solid = normal speed; hollow = fast mode; a thin line joins it to the same config at normal speed. ⚡ also marks fast mode.</span><span>Frontier points and selected pipeline triangles are labelled; hover, tap or focus a point or a key row for the rest.</span></div>
<div class="tabs"><input type="radio" name="pset" id="pset-all" checked><label for="pset-all">Main ladder</label><input type="radio" name="pset" id="pset-hard"><label for="pset-hard">Rescue set + pipelines</label>
<div class="tab tab-all">
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
{{w_sets}}
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate. Whiskers: {{ci_level}} confidence interval (bootstrap).</li>
<li>The three cheapest points miss about {{cheap_miss_words}}: luna-low {{luna_low_pass}}, luna-low-bare {{luna_low_bare_pass}}, luna-medium {{luna_medium_pass}}. (luna-low-bare = luna-low with Codex's own system prompt removed.)</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Best speed for the money among configs passing ≥{{min_pass}}: {{w_front_speed}}.</li>
<li>Pipelines ran only on the rescue set: see the "Rescue set + pipelines" tab.</li>
</ul>
</div>
<div class="tab tab-hard">
<div class="chart"><h3>Rescue set: pass rate vs $ per pass</h3><p class="sub">{{w_rescue_subtitle}}</p>{{w_hard_pass_cost}}</div>
<ul class="tight small">
<li>Best trade-offs, cheapest first: {{w_hard_front_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ Rescue set: speed vs $ per pass</h3><p class="sub">{{w_rescue_subtitle}}</p>{{w_hard_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_hard_front_speed}}.</li>
</ul>
</div>
</div>
{{w_sets}}
</section>
<section id="fail">
<h2><span class="num"></span>🟥 Where they fail</h2>
<p class="small">{{worst_failure}}. Cells show passed/attempted: green = all passed, amber = more than half, red = half or fewer; dash = not run. Scroll sideways for more configs. E/M/H = my LeetCode difficulty guess.</p>
{{w_grid}}
<ul class="tight small">
<li>p04 taller_within: luna-low, luna-medium and luna-low-bare each passed only {{p04_passes}} of {{repeats}}.</li>
<li>haiku-low: main ladder — {{hl_main_failures}}; L7 set — {{hl_l7_failures}}.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
<p class="small">sol61-high is the Codex routing pick; haiku-high is the cheapest config with no misses across the main ladder, L7 and repo tasks.</p>
{{w_short_table}}
<ul class="tight small">
<li>★ = a Winner pick (sol61-high on Codex, haiku-high on Claude); budget pick = cheapest config passing {{budget_pass}} or more.</li>
<li><b>0 misses</b>: every attempt passed; “cheapest” compares those rows within the set. “one miss” or “missed N” counts failed attempts.</li>
<li>beaten = another row is as cheap and passes as often; pricier, passes more = a trade-off; avoid = below {{min_pass}}.</li>
<li>Purple dot = pipeline (two models); → = a second step; →retry uses the same model twice.</li>
<li>~ / proxy = Codex $ estimated from tokens and list prices. Claude $ = the part billed to the Claude CLI; Codex calls bill Codex.</li>
<li>Click a header to sort within each set; on a phone, scroll sideways for the verdict.</li>
<li>haiku-medium had 0 misses on the rescue set (its {{rescue_n}} main-run attempts on those problems, not a new run).</li>
</ul>
<details><summary>Full table with intervals and tail latency</summary>
{{table:result_detail}}
<ul class="tight small">
<li>pass@1 is the fraction of individual attempts passing all hidden tests.</li>
<li>p90 = time within which {{p90_percent}} of calls finished.</li>
<li>≥N% (all passed) = lower {{ci_level}} bound when nothing failed.</li>
</ul>
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3>{{w_fast}}</div>
<ul class="tight small">
<li>Default → ⚡ pairs: sol61-high and astra-medium, main ladder and L7; same model and effort, default and priority service tiers. All passed.</li>
<li>Fast-mode $ uses {{fm_mult}} the list price (the pricing-page multiplier, not a measured bill).</li>
</ul>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<p class="small">Trimming luna-low's Codex system prompt cuts input from {{luna_low_in}} to {{luna_low_bare_in}} tokens per call ({{in_cut}} less); haiku-low uses {{haiku_low_in}}.</p>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Token floor = input added by Codex’s harness before the task.</li>
<li>Bars show mean input per call, including the task, so prompt length counts.</li>
<li>Solid = served from cache; faded = uncached.</li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">haiku-medium had no rescue-set misses; the best luna repair pipeline cost {{hm_vs_pipe_x}} as much.</p>
<div class="chart floor"><h3>Rescue set: passes, $ per pass, median seconds</h3>{{w_pipes}}</div>
<p class="small">{{w_rescue_subtitle}}</p>
<ul class="tight small">
<li>Haiku reviewing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}.</li>
<li>Example checks leak: a fresh luna-high-bare run had {{g_hi_bad}} bad answers; checks caught {{g_hi_fixed}} (Haiku fixed {{g_hi_fixed_words}}), missed {{g_hi_missed}}. Without checks: {{r_luna_high_bare_miss}} bad answers.</li>
<li>Haiku on failed samples: sol61-high {{r_sol61_high_haiku_on_fail_k}}, astra-medium {{r_astra_medium_haiku_on_fail_k}}; no repairs fired. Fast-mode pipelines equal their builders.</li>
<li>Planning first helped luna-low ({{r_luna_low_k}} → {{r_haiku_low_plan_luna_low_k}}), not luna-high-bare ({{r_luna_high_bare_k}} either way). Both Haiku-plan pipelines cost more than Haiku checking after.</li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>✅ CONCLUSION</h2>
<b>Use sol61-high when Codex has quota. Use haiku-low when it does not; use haiku-high when a miss would be costly or you need speed.</b>
<ol class="recs">
<li>Codex has quota: sol61-high. Run the worked examples after; haiku-low fixes only if they fail ({{claude_zero}} Claude).</li>
<li>Claude only (Codex out): haiku-low first. If its answer fails the problem's worked examples, or a wrong answer would be costly, use haiku-high instead.</li>
<li>Need it faster than sol61-high ({{x_sol61_high_med}} s)? haiku-high: {{hh_med}} s, never missed, {{hh_upp}} per pass.</li>
<li>Must stay on Codex and need speed? sol61-high fast mode: {{ff_s61_med}} s, {{ff_s61_upp}} per pass, about {{ff_s61_x}} the Codex usage.</li>
<li>Fastest at any price? astra-medium fast mode: {{ff_ast_med}} s, {{ff_ast_upp}} per pass.</li>
<li>Want a bigger Claude model with zero misses? sonnet-medium: also never missed, {{sonnet_medium_med}} s, but {{sm_vs_hh_x}} haiku-high's cost per pass.</li>
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
<section class="notes" id="notes">
<h2><span class="num"></span>Notes: caveats, code quality, appendix</h2>
<details><summary>⚠️ Caveats</summary>
<ul class="tight">
<li>Small sample: read the intervals before the point estimates.</li>
<li>† Exploratory means added after seeing the main-run results, outside the original comparison. {{n_exploratory}} configs were added: {{exploratory_names}}, including the Winner’s sol61-high and astra-medium.</li>
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
<li>Latency is CLI wall clock, up to {{lanes}} calls in flight on one host.</li>
<li>One run in time; hosted models change.</li>
</ul>
</details>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
<p class="small">{{quality_fast_note}}</p>
<p class="small">Complexity = max cyclomatic complexity per function (radon); lint = ruff warnings; worse growth = time-growth exponent more than {{growth_margin}} above the reference’s; time vs ref / mem vs ref = run time and memory divided by the reference solution's; below {{ref_unit}} is faster or leaner.</p>
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
{{w_everything}}
</section>
