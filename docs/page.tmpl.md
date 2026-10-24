<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a><a href="#notes">Notes</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p><b>Use Codex quota first. Choose Haiku for savings, Sonnet for speed.</b></p>
{{w_winner}}
<details class="small names"><summary>Model names</summary>
<ul class="tight small">
<li>Claude models: haiku and sonnet.</li>
<li>Codex models: luna, sol and astra (OpenAI).</li>
<li>Suffix = effort: low / medium / high.</li>
<li>{{model_names}}.</li>
</ul>
</details>
{{w_legend}}
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
<li>Sets:<ul>
<li>Main ladder: {{n_problems}} problems, {{repeats}} tries each. Total: {{n_calls}} calls.</li>
<li>L7: {{n_l7}} problems, {{repeats}} tries each. Total: {{l7_n}} calls.</li>
<li>{{set_label_title}}: the {{n_rescue_problems}} main-ladder problems luna-low missed most.</li>
<li>Chosen after the main run. Each row has {{rescue_n}} attempts.</li>
<li>Repo tasks: {{n_tasks}} edits, {{agent_repeats}} tries each. Total: {{ag_n}} calls.</li>
</ul></li>
<li>Pass = every hidden test passes: the fixed cases, random cases checked against the reference solution, and large cases for speed.</li>
<li>Sample tests = the worked examples in the problem text. Cheap to run, and the model can see them.</li>
<li>Claude $ from the CLI. Codex $ = tokens × list price; ~ means estimated from tokens, not billed. {{ci_level}} intervals from {{n_boot}} bootstrap resamples (how much the pass rate would wobble on a rerun).</li>
<li>Run by Wren, a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
</ul>
<details><summary>Exact commands</summary>
<p class="small">Run {{run_id}}.</p>
<ul class="tight small cmds">
{{w_flags}}
<li>luna-low-bare and luna-high-bare add the stripped harness (the Codex CLI’s own system prompt and tool text, trimmed by bench/trim_probe.py). Every luna-high row on the {{set_label}} uses it.</li>
</ul>
</details>
<p class="small"><b>Q: Does Claude's harness make Codex look bad?</b><br><b>A: {{hb_answer}}</b> {{hb_detail}}</p>
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
<div class="tabs"><input type="radio" name="pset" id="pset-all" checked><label for="pset-all">Main ladder</label><input type="radio" name="pset" id="pset-hard"><label for="pset-hard">{{set_label_title}} + pipelines</label>
<div class="tab tab-all">
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
{{w_sets}}
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate. Whiskers: {{ci_level}} confidence interval (bootstrap).</li>
<li>The three cheapest points miss about {{cheap_miss_words}}: luna-low {{luna_low_pass}}, luna-low-bare {{luna_low_bare_pass}}, luna-medium {{luna_medium_pass}}. (luna-low-bare = luna-low with Codex's own system prompt removed.)</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_front_speed}}.</li>
<li>Hollow pipeline points use the {{set_label}}. See the "{{set_label_title}} + pipelines" tab.</li>
</ul>
</div>
<div class="tab tab-hard">
<div class="chart"><h3>{{set_label_title}}: pass rate vs $ per pass</h3><p class="sub">{{w_rescue_subtitle}}</p>{{w_hard_pass_cost}}</div>
<ul class="tight small">
<li>Best trade-offs, cheapest first: {{w_hard_front_pass}}.</li>
</ul>
<div class="chart"><h3>⏱️ {{set_label_title}}: speed vs $ per pass</h3><p class="sub">{{w_rescue_subtitle}}</p>{{w_hard_speed_cost}}</div>
<ul class="tight small">
<li>Best trade-offs: {{w_hard_front_speed}}.</li>
<li><a href="#notation">See Notation.</a></li>
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
<p class="small">sol61-high is the Codex pick. haiku-high is the cheapest config without misses across the ladder, L7 and repo tasks.</p>
{{w_short_table}}
<ul class="tight small">
<li>★ = Winner pick, or cheapest row without misses in its group.</li>
<li>Budget pick = cheapest at {{budget_pass}}+. Avoid = below {{min_pass}}.</li>
<li>Beaten = another row is as cheap and passes as often. Trade-off = pricier, passes more.</li>
<li>Claude $: “all” means the whole cost. Pipeline rows show the Haiku share per pass.</li>
<li>Click a header to sort within a group. <a href="#notation">Symbols: see Notation.</a></li>
<li>haiku-medium's {{set_label}} row reuses its {{rescue_n}} main-run attempts.</li>
<li>sol61-high and astra-medium →H fail never called Haiku. Their ⚡ rows replay cached answers.</li>
<li>Those pipeline measurements remain in Pipelines and the chart explorer.</li>
</ul>
<details><summary>Full table: intervals and p90</summary>
<p class="small">Intervals show pass-rate uncertainty. p90 covers slower calls.</p>
{{w_full_table}}
<ul class="tight small">
<li>Each config ran {{n_calls}} calls. † = exploratory, added after the main run.</li>
<li>pass@1 is the fraction of individual attempts passing all hidden tests.</li>
<li>p90 = time within which {{p90_percent}} of calls finished.</li>
<li>≥N% (all passed) = lower {{ci_level}} bound when nothing failed.</li>
</ul>
<p class="small">Fast mode passed everything on both sets.</p>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3>{{w_fast}}</div>
<ul class="tight small">
<li>Pairs compare sol61-high and astra-medium at normal speed and ⚡.</li>
<li>The model and effort stay the same. Both the main ladder and L7 passed everything.</li>
<li>Fast-mode $ uses {{fm_mult}} list price. This multiplier comes from the pricing page.</li>
<li>Codex $ estimates use tokens, not measured bills. <a href="#notation">See Notation.</a></li>
</ul>
</details>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<p class="small">Trimming luna-low's Codex system prompt cuts mean input by {{in_cut}}.</p>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Token floor = input added by Codex’s harness before the task.</li>
<li>Bars show mean input per call, including the task.</li>
<li>Solid = served from cache. Faded = uncached.</li>
<li>Low-context rows use trimmed prompts. All these runs had tools off.</li>
<li><a href="#notation">See Notation.</a></li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">Pipelines were run on the {{set_label}} only.</p>
<div class="chart floor"><h3>Passes, $ per pass, median seconds</h3>{{w_pipes}}</div>
<ul class="tight small">
<li>Haiku reviewing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}.</li>
<li>sol61-high and astra-medium →H fail never called Haiku. Their ⚡ rows replay cached answers.</li>
<li>Low-context rows use trimmed prompts. <a href="#notation">See Notation.</a></li>
</ul>
<p class="small">{{w_rescue_subtitle}}</p>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>✅ CONCLUSION</h2>
<b>Use Codex quota first. Choose Haiku for savings, Sonnet for speed.</b>
<ul class="tight">
<li>sol61-high never missed on the {{main_set_label}}, {{l7_set_label}} or repo tasks. With subscription quota, its cost per pass is {{claude_zero}}. Its Claude bill stays {{claude_zero}}. Check worked examples; haiku-low fixes failures. On the {{set_label}}, Haiku never ran: {{r_sol61_high_haiku_on_fail_k}}.</li>
<li>Codex out? haiku-low is cheapest at {{budget_pass}}+ passing. A costly miss? Choose haiku-high. It passed {{hh_k}} on the {{main_set_label}}. It passed {{hh_hk}} on the {{l7_set_label}}. Repo tasks: {{ag_hh_k}}. Claude costs come from the CLI.</li>
<li>sonnet-medium never missed across these sets. Its cost per pass is {{sm_vs_hh_x}} haiku-high's. sol61-high ⚡ charges {{fm_mult}} list price without increasing token counts.</li>
<li>{{hb_conclusion}} luna-low: {{hb_claude_luna_low}} in our one-shot runner. Codex CLI: {{hb_codex_luna_low}}. haiku-low: {{hb_claude_haiku_low}} in our one-shot runner. Claude Code: {{hb_codex_haiku_low}}. Gap shift: {{hb_diff}}, below the pre-set bar. Supported range: {{hb_ci}}.</li>
<li>Avoid luna-low or luna-medium alone. The best luna fix is luna-high-bare →H all. It passed {{r_luna_high_bare_haiku_review_all_k}} on the {{set_label}}. It costs {{hm_vs_pipe_x}} as much as haiku-medium alone.</li>
</ul>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<details><summary>🎛️ Explorer and more charts</summary>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run}}
</details>

<p class="small"><a href="#notation">See Notation.</a></p>
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
<p class="small">{{fm_n}} attempts use the {{set_label}}, with {{repeats}} repeats.
The control is a separate default-tier sol61-high run, repeats {{fm_rep_lo}}–{{fm_rep_hi}}.
Its {{fm_ctrl_s}} s differs from the Results row.
That row uses repeats {{repeat_lo}}–{{repeats}}.</p>
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
<li>The example check lets bad answers through.
<ul>
<li>A fresh luna-high-bare run had {{g_hi_bad}} bad answers.</li>
<li>The check caught {{g_hi_fixed}}. Haiku fixed {{g_hi_fixed_words}}.</li>
<li>It missed {{g_hi_missed}}: they passed examples but failed hidden tests.</li>
<li>The plain luna-high-bare run had {{r_luna_high_bare_miss}} bad answers.</li>
</ul></li>
<li>sol61-high and astra-medium never needed Haiku.
<ul>
<li>sol61-high → Haiku if examples fail: {{r_sol61_high_haiku_on_fail_k}}. No repair ran.</li>
<li>astra-medium → Haiku if examples fail: {{r_astra_medium_haiku_on_fail_k}}. No repair ran.</li>
<li>⚡ rows: same result, replayed from cached answers.</li>
</ul></li>
<li>A Haiku plan first helped luna-low.
<ul>
<li>Before planning: {{r_luna_low_k}}. With planning: {{r_haiku_low_plan_luna_low_k}}.</li>
<li>luna-high-bare passed {{r_luna_high_bare_k}} either way.</li>
<li>Both plan-first pipelines cost more than fixing afterwards.</li>
</ul></li>
<li>L7 set (p13–p15 × {{repeats}}): haiku-low {{l7_hl_k}} at {{l7_haiku_low_upp}} per pass, sonnet-medium {{l7_sm_k}} at {{l7_sonnet_medium_upp}}.</li>
<li>Escalation (retrying weak problems at higher effort): on {{esc_problems}}, luna-high passed {{esc_k}} where {{esc_vs}} passed {{esc_base}}.</li>
<li>{{set_label_title}}: {{rescue_n}} attempts per row.
→H fail: {{r_luna_high_bare_haiku_on_fail_k}} at {{r_luna_high_bare_haiku_on_fail_upp}} per pass.
→retry: {{r_luna_high_bare_retry_on_fail_k}} at {{r_luna_high_bare_retry_on_fail_upp}} per pass.</li>
<li>Pilot ({{pilot_problems}} well-known LeetCode problems): every config passed, so it ranked nothing. The fast-mode pilot ({{fast_problems}} problems × {{fast_rounds}} rounds) used {{fast_mult}} the list price: sol61-low got faster ({{fast_sol_def}}s → {{fast_sol_fast}}s), luna-low did not ({{fast_luna_def}}s → {{fast_luna_fast}}s); the only fast-mode data for low effort.</li>
<li>{{set_label_title}}: {{rescue_n}} attempts per row.
The original luna-low→H all run passed {{r_luna_low_haiku_low_repair_k}}.
Its prompt was not kept.
The rerun from committed code passed {{r_luna_low_haiku_review_all_k}}.</li>
<li>Repo tasks ({{n_tasks}} tasks × {{agent_repeats}} runs, with tools): every config passed {{ag_k}}. $ per run: luna-low {{ag_luna_low_usd}}, haiku-low {{ag_haiku_low_usd}}, sonnet-medium {{ag_sonnet_medium_usd}}, sol61-medium {{ag_sol61_medium_usd}}, haiku-high {{ag_haiku_high_usd}}, sol61-high {{ag_sol61_high_usd}}, astra-medium {{ag_astra_medium_usd}}.</li>
</ul>
</details>
{{w_everything}}
</section>
