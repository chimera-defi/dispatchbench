<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a><a href="#notes">Notes</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p><b>Use sol61-high when Codex has quota. Use haiku-low when it does not; use haiku-high when a miss would be costly or you need speed.</b></p>
<p class="small names">Names: haiku and sonnet are Claude; luna, sol and astra are Codex (OpenAI). Suffix = effort (low / medium / high). {{model_names}}. Symbols: see Notation below.</p>
{{w_legend}}
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
<p class="small">Every config got the same new problems and hidden tests. Tools were off: no code runs, file reads or search.</p>
<details><summary>📚 Problems by round (Easy/Medium/Hard)</summary>
<ul class="tight small">
<li>We wrote these problems for this bench.</li>
<li>Each LeetCode link is the closest analogue I found by hand.</li>
<li>Pilot links say "source": those problems come from LeetCode.</li>
<li>Easy/Medium/Hard is my guess at LeetCode difficulty.</li>
<li>Rungs follow this bench's own difficulty order.</li>
<li>The two can disagree:<ul>{{badge_disagreement_items}}</ul></li>
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>Total spend: {{claude_usd}} on Claude; estimated {{codex_usd}} of Codex quota.</li>
<li>Sets:<ul>
<li>Main ladder: {{n_problems}} problems, {{repeats}} tries each. Total: {{n_calls}} calls.</li>
<li>L7: {{n_l7}} problems, {{repeats}} tries each. Total: {{l7_n}} calls.</li>
<li>{{set_label_title}}: the {{n_rescue_problems}} main-ladder problems luna-low missed most.</li>
<li>Chosen after the main run. Each row has {{rescue_n}} attempts.</li>
<li>Repo tasks: {{n_tasks}} edits, {{agent_repeats}} tries each. Total: {{ag_n}} calls.</li>
</ul></li>
<li>Pass = every hidden test passes:<ul>
<li>Fixed cases.</li>
<li>Random cases checked against the reference solution.</li>
<li>Large cases for speed.</li>
</ul></li>
<li>Sample tests = the worked examples in the problem text. The model can see them.</li>
<li>They are cheap to run.</li>
<li>Claude $: what the CLI reports.</li>
<li>Codex $: tokens × list price. ~ marks estimates, not bills.</li>
<li>{{ci_level}} intervals from {{n_boot}} bootstrap resamples: how much a rerun's pass rate could vary.</li>
<li>Run by Wren, a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
</ul>
<details><summary>Exact commands</summary>
<ul class="tight small cmds">
{{w_flags}}
<li><code>-bare</code> trims Codex's system prompt and tool text using <code>bench/trim_probe.py</code>.</li>
<li>This applies to luna-low-bare and luna-high-bare.</li>
<li>Every luna-high row on the {{set_label}} uses it.</li>
</ul>
</details>
<p class="small"><b>Q: Does our one-shot runner make Codex look bad?</b></p>
<ul class="tight small">
<li><b>A: {{hb_answer}}</b></li>
<li>{{hb_takeaway}}</li>
<li>{{hb_detail}}</li>
<li>Codex built and finished the agent-CLI comparison. It had {{hb_errors}} harness errors and no timeouts.</li>
</ul>
<p class="small">Harness = the program that sends the problem to the model and grades the answer.</p>
<table><caption>Passed / attempted, paired fairness comparison</caption><thead><tr><th>Model</th><th>our one-shot runner</th><th>vendor agent CLI (runs code, retries)</th></tr></thead><tbody>
<tr><td>luna-low</td><td>{{hb_claude_luna_low}}</td><td>{{hb_codex_luna_low}}</td></tr>
<tr><td>haiku-low</td><td>{{hb_claude_haiku_low}}</td><td>{{hb_codex_haiku_low}}</td></tr>
</tbody></table>
<p class="small">Vendor agent CLI: luna-low uses Codex CLI; haiku-low uses Claude Code.</p>
<p class="small">Codex used its own CLI in the main benchmark: personal settings ignored, tools off.</p>
<p class="small">Runner details, Codex behaviour and model strengths: see the <a href="#appendix">Appendix</a>.</p>
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
<p class="small">{{worst_failure}}.</p>
<ul class="tight small">
<li>Cells = passed/attempted. Green: all passed. Amber: more than half. Red: half or fewer.</li>
<li>Dash: not run. Scroll sideways for more configs.</li>
<li>E/M/H = my LeetCode difficulty guess.</li>
</ul>
{{w_grid}}
<ul class="tight small">
<li>p04 taller_within: luna-low, luna-medium and luna-low-bare each passed only {{p04_passes}} of {{repeats}}.</li>
<li>haiku-low never returned a wrong answer on the main ladder or L7.</li>
<li>Its timeout and crash counts are in the <a href="#appendix">Appendix</a>.</li>
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
<li>haiku-medium's {{set_label}} row reuses its {{rescue_n}} main-run attempts.</li>
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
<li><a href="#notation">See Notation.</a></li>
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
<li><a href="#notation">See Notation.</a></li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">Pipelines were run on the {{set_label}} only.</p>
<div class="chart floor"><h3>{{set_label_title}}: passes, $ per pass, median seconds</h3>{{w_pipes}}</div>
<p class="small">{{w_rescue_subtitle}}</p>
<ul class="tight small">
<li>Haiku reviewing every luna-high-bare answer: {{r_luna_high_bare_haiku_review_all_k}}.</li>
<li>Example checks leak: a fresh luna-high-bare run had {{g_hi_bad}} bad answers; checks caught {{g_hi_fixed}} (Haiku fixed {{g_hi_fixed_words}}), missed {{g_hi_missed}}. Without checks: {{r_luna_high_bare_miss}} bad answers.</li>
<li>Haiku on failed samples: sol61-high {{r_sol61_high_haiku_on_fail_k}}, astra-medium {{r_astra_medium_haiku_on_fail_k}}; no repairs fired. Fast-mode pipelines equal their builders.</li>
<li>Planning first helped luna-low ({{r_luna_low_k}} → {{r_haiku_low_plan_luna_low_k}}), not luna-high-bare ({{r_luna_high_bare_k}} either way). Both Haiku-plan pipelines cost more than Haiku checking after.</li>
<li><a href="#notation">See Notation.</a></li>
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

<p class="small"><a href="#notation">See Notation.</a></p>
</section>
<section class="notes" id="notes">
<h2><span class="num"></span>Notes: caveats, code quality, appendix</h2>
<details><summary>⚠️ Caveats</summary>
<ul class="tight">
<li>Small sample: read the intervals before the point estimates.</li>
<li>† = exploratory: added after the main run, outside the original comparison.</li>
<li>We added {{n_exploratory}} configs:<ul>{{exploratory_items}}</ul></li>
<li>The Winner's sol61-high is one of them.</li>
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
<li>Latency is CLI wall clock.</li>
<li>We ran up to {{lanes}} calls at once on one host.</li>
<li>One run in time; hosted models change.</li>
</ul>
</details>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
<ul class="tight small">{{quality_fast_items}}</ul>
<ul class="tight small">
<li>Complexity = maximum cyclomatic complexity per function (radon).</li>
<li>Lint = ruff warnings per solution.</li>
<li>Worse growth = time-growth exponent more than {{growth_margin}} above the reference's.</li>
<li>Time vs ref = run time divided by the reference solution's.</li>
<li>Mem vs ref = memory divided by the reference solution's.</li>
<li>Below {{ref_unit}} is faster or leaner.</li>
</ul>
<ul class="tight">
<li>Scored: main-ladder passing solutions, {{q_rows}} rows.</li>
<li>All {{n_solutions}} solutions are in <code>results/solutions</code>.</li>
<li>On {{q_worst_problem}}, {{q_slow_n}} solutions run slower than the reference.</li>
<li>The smallest slowdown is {{q_slow_lo}}.</li>
<li>They come from {{q_slow_cfgs}} configs.</li>
<li>The worst is one {{q_worst_cfg}} solution at {{q_worst_x}}.</li>
</ul>
</details>
<details><summary>⚡ Codex fast mode and xhigh</summary>
<ul class="tight small">
<li>{{fm_n}} attempts use the {{set_label}}, with {{repeats}} repeats.</li>
<li>The control is a separate default-tier sol61-high run.</li>
<li>It uses repeats {{fm_rep_lo}}–{{fm_rep_hi}}.</li>
<li>Its {{fm_ctrl_s}} s differs from the Results row.</li>
<li>That row uses repeats {{repeat_lo}}–{{repeats}}.</li>
</ul>
{{table:fastmode}}
<ul class="tight">
<li>Fast mode: same passes, same code quality.</li>
<li>It was {{fm_faster}} faster per call.</li>
<li>Median seconds: {{fm_fast_s}} fast; {{fm_ctrl_s}} default.</li>
<li>Priced at {{fm_mult}} list: the pricing-page multiplier, not a bill.</li>
<li>xhigh: same passes, {{fm_x_cost}} the cost.</li>
<li>It was slower, with no better code.</li>
<li>Blind read: {{bl_n}} solutions.</li>
<li>All {{bl_blocks}} blocks were sonnet-medium.</li>
</ul>
<p class="small">{{blind_caption}}</p>
{{table:blind}}
</details>
<details id="appendix"><summary>📎 Appendix</summary>
<h3>Harnesses: which model does better at what?</h3>
<ul class="tight small">
<li>{{hb_accuracy}}</li>
<li>{{hb_speed}}</li>
<li>These pooled calls include extra runs beyond the paired fairness comparison.</li>
</ul>
{{table:harness_strengths}}
<ul class="tight small">
<li>Our one-shot runner answers once, tools off.</li>
<li>Codex built the vendor-CLI runner.</li>
<li>It runs each model inside its vendor's agent CLI.</li>
<li>That tool loop runs code and revises answers.</li>
<li>The mechanisms differ, not just in who built them.</li>
<li>Both runners tested luna-low and haiku-low.</li>
<li>Paired comparison: {{hb_n_problems}} hard problems × {{hb_repeats}} repeats.</li>
<li>Bias means a change in the gap between the models' pass rates.</li>
<li>The confidence interval contains plausible bias values: {{hb_ci}}.</li>
<li>{{hb_uncertainty}}</li>
<li>The agent-CLI run had {{hb_errors}} harness errors and no timeouts.</li>
<li>It took about {{hb_minutes}} minutes of wall time for the recorded calls.</li>
<li>Codex also answered through its own CLI in the main benchmark.</li>
<li>We ignored personal settings and disabled tools.</li>
<li>The <code>luna-*-bare</code> rows test how much Codex's system prompt and tool text matter.</li>
<li>On repo tasks the host's <code>AGENTS.md</code> triggered extra shell commands:<ul>
<li>sol61-medium: {{host_sol61_medium}} of {{shell_sol61_medium}} commands.</li>
<li>luna-low: {{host_luna_low}} of {{shell_luna_low}} commands.</li>
</ul></li>
<li>Codex's measured time includes those extra commands.</li>
</ul>
<h3>Failures and later runs</h3>
<p class="small">haiku-low misses:</p>
{{table:haiku_failures}}
<p class="small">Too slow = exceeding the grader's time limit for that case.</p>
<ul class="tight">
<li>L7 set: {{repeats}} tries per problem.</li>
<li>Problems:<ul>{{l7_problem_items}}</ul></li>
<li>haiku-low passed {{l7_hl_k}}. Cost: {{l7_haiku_low_upp}} per pass.</li>
<li>sonnet-medium passed {{l7_sm_k}}. Cost: {{l7_sonnet_medium_upp}} per pass.</li>
<li>Escalation = rerun weak problems at higher effort.</li>
<li>Problems:<ul>{{escalation_problem_items}}</ul></li>
<li>luna-high passed {{esc_k}}.</li>
<li>{{esc_vs}} had passed {{esc_base}}.</li>
<li>Retrying luna-high-bare itself passed as often as a Haiku fix:<ul>
<li>Haiku fixes failed examples: {{r_luna_high_bare_haiku_on_fail_k}}.</li>
<li>Cost: {{r_luna_high_bare_haiku_on_fail_upp}} per pass.</li>
<li>Same-model retry: {{r_luna_high_bare_retry_on_fail_k}}.</li>
<li>Cost: {{r_luna_high_bare_retry_on_fail_upp}} per pass.</li>
</ul></li>
<li>These rows use the {{set_label}}: {{rescue_n}} attempts each.</li>
<li>Example checks can miss bad answers:<ul>
<li>A fresh luna-high-bare run had {{g_hi_bad}} bad answers.</li>
<li>Checks caught {{g_hi_fixed}}. Haiku fixed {{g_hi_fixed_words}}.</li>
<li>Checks missed {{g_hi_missed}}.</li>
<li>The run without checks had {{r_luna_high_bare_miss}} bad answers.</li>
</ul></li>
<li>Haiku fixes failed examples:<ul>
<li>sol61-high passed {{r_sol61_high_haiku_on_fail_k}}.</li>
<li>astra-medium passed {{r_astra_medium_haiku_on_fail_k}}.</li>
<li>No repairs fired. Fast-mode pipelines equal their builders.</li>
</ul></li>
<li>Planning first:<ul>
<li>luna-low passed {{r_luna_low_k}} without a plan.</li>
<li>With a Haiku plan: {{r_haiku_low_plan_luna_low_k}}.</li>
<li>luna-high-bare passed {{r_luna_high_bare_k}} either way.</li>
<li>Both Haiku-plan pipelines cost more than Haiku checking after.</li>
</ul></li>
<li>Pilot: {{pilot_problems}} well-known LeetCode problems.</li>
<li>Every config passed, so it ranked nothing.</li>
<li>Fast-mode pilot: {{fast_problems}} problems, {{fast_rounds}} rounds.</li>
<li>It used {{fast_mult}} list price.</li>
<li>sol61-low got faster: {{fast_sol_def}} s → {{fast_sol_fast}} s.</li>
<li>luna-low did not: {{fast_luna_def}} s → {{fast_luna_fast}} s.</li>
<li>This is the only fast-mode data at low effort.</li>
<li>The original luna-low → Haiku-fixes-all run passed {{r_luna_low_haiku_low_repair_k}}.</li>
<li>Its prompt was not kept.</li>
<li>The rerun from committed code passed {{r_luna_low_haiku_review_all_k}}.</li>
<li>Both use the {{set_label}}: {{rescue_n}} attempts per row.</li>
<li>Repo tasks: {{n_tasks}} edits, {{agent_repeats}} runs each, with tools.</li>
<li>Every config passed {{ag_k}}.</li>
<li>Cost per run:<ul>
<li>luna-low: {{ag_luna_low_usd}}.</li>
<li>haiku-low: {{ag_haiku_low_usd}}.</li>
<li>haiku-high: {{ag_haiku_high_usd}}.</li>
<li>sonnet-medium: {{ag_sonnet_medium_usd}}.</li>
<li>sol61-medium: {{ag_sol61_medium_usd}}.</li>
<li>sol61-high: {{ag_sol61_high_usd}}.</li>
<li>astra-medium: {{ag_astra_medium_usd}}.</li>
</ul></li>
</ul>
</details>
{{w_everything}}
</section>
