<header class="head">
<h1>Which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#method">How it was run</a><a href="#pareto">Cost vs accuracy</a><a href="#fail">Where they fail</a><a href="#results">Results</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#conclusion">Conclusion</a><a href="#extras">More charts</a><a href="#notes">Notes</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p><b>Use Codex first: on a subscription its calls cost {{claude_zero}} cash. Paying per call? Haiku is cheapest. Need speed? Sonnet.</b></p>
{{w_winner}}
<details class="small names"><summary>Model names</summary>
<ul class="tight small">
<li>Config = one model at one effort level, e.g. haiku-low.</li>
<li>Claude models: haiku and sonnet.</li>
<li>Codex models: luna, sol and astra (OpenAI).</li>
<li>Suffix = effort: low / medium / high / xhigh (a step above high).</li>
<li>{{model_names}}.</li>
</ul>
</details>
{{w_legend}}
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Every config (model + effort) got the same new problems and hidden tests. Tools were off: no code runs, file reads or search.</p>
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
<li>Function and agentic sets cost {{claude_usd}} on Claude; Codex quota use was estimated at {{codex_usd}}. These totals cover function and agentic sets only. We excluded pilot, harness-bias, trim and {{set_label}} pipeline runs.</li>
<li>Sets:<ul>
<li>{{main_set_label}}: {{n_problems}} problems, {{repeats}} tries each. Total: {{n_calls}} calls.</li>
<li>{{l7_set_label}}: {{n_l7}} problems, {{repeats}} tries each. Total: {{l7_n}} calls.</li>
<li>{{set_label_title}}: the {{n_rescue_problems}} main-ladder problems luna-low missed most, chosen after the main run. Each config tried {{n_rescue_problems}} problems, {{repeats}} times each. Each config made {{rescue_n}} calls.</li>
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
<p class="small">Harness = program that sends the problem to the model and grades the answer.</p>
<p class="small"><b>Q: Does our one-shot runner make Codex look bad?</b></p>
<ul class="tight small">
{{w_hb_qa}}
<li>Codex built and finished the agent-CLI comparison. It had {{hb_errors}} harness errors and no timeouts.</li>
</ul>
<table><caption>Passed / attempted on {{hb_n_problems}} hard problems × {{hb_repeats}} repeats (not the {{main_set_label}})</caption><thead><tr><th>Model</th><th>our one-shot runner</th><th>vendor agent CLI (runs code, retries)</th></tr></thead><tbody>
<tr><td>luna-low</td><td>{{hb_claude_luna_low}}</td><td>{{hb_codex_luna_low}}</td></tr>
<tr><td>haiku-low</td><td>{{hb_claude_haiku_low}}</td><td>{{hb_codex_haiku_low}}</td></tr>
</tbody></table>
<p class="small">Vendor agent CLI: luna-low uses Codex CLI; haiku-low uses Claude Code.</p>
<p class="small">Codex used its own CLI in the main benchmark: personal settings ignored, tools off.</p>
<p class="small">Runner details, Codex behaviour and model strengths: see the <a href="#appendix">Appendix</a>.</p>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<p class="small">haiku-high passes {{haiku_high_pass}} at {{haiku_high_upp}} per pass. sol61-high also passes {{sol61_high_pass}} at ~{{sol61_high_upp}} per pass. It costs {{claude_zero}} on Codex quota. luna-low and luna-medium cost less but miss about {{cheap_miss_words}}.</p>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="ring"></span>Pareto frontier</span><span>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet. Triangles = luna · ◆ sol · ★ astra. Luna triangle direction = effort: up low, right medium, down high. Alternate Codex colour = the older gpt-{{older_generation}} models (luna56, sol56).</span><span>Filled = normal speed. Hollow (⚡) = fast mode, joined by a thin line to its normal-speed point. Dashed edge = bare prompt.</span><span>Labels mark frontier points, the picks named above, and older-generation and fast-mode points. Pipeline views label frontier points and pipelines. Hover, tap or focus a point or key row for the rest.</span></div>
<ul class="tight small">
<li>Purple line = best trade-offs: nothing is both cheaper and more accurate.</li>
<li>Whiskers: {{ci_level}} confidence interval (bootstrap).</li>
</ul>
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
<ul class="tight small">
<li>The three cheapest points miss about {{cheap_miss_words}}.</li>
<li>luna-low {{luna_low_pass}}. luna-low-bare {{luna_low_bare_pass}}. luna-medium {{luna_medium_pass}}.</li>
<li>luna-low-bare = luna-low with Codex's own system prompt removed.</li>
</ul>
<div class="chart"><h3>⏱️ Speed vs $ per pass</h3><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div>
<ul class="tight small">
<li>Pipelines are on the "{{set_label_title}} + pipelines" tab.</li>
</ul>
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
<li>haiku-low never gave a wrong answer.</li>
<li>Its {{hl_main_misses}} main-ladder misses: {{hl_main_timeouts}} too slow. {{hl_main_crashes}} crash.</li>
<li>Its {{l7_hl_fail}} L7 misses: all too slow.</li>
</ul>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
<p class="small">sol61-high is the Codex pick. haiku-high is the cheapest config without misses across the ladder, L7 and repo tasks.</p>
<p class="small">Verdict key: {{verdict_key}}</p>
{{w_short_table}}
<ul class="tight small">
<li>Claude $ column: all = every dollar of that row went to Claude.</li>
<li>Pipeline rows show only the Haiku share.</li>
<li>Click a header to sort within a group. <a href="#notation">Symbols: see Notation.</a></li>
<li>haiku-medium's {{set_label}} row reuses its {{rescue_n}} main-run attempts.</li>
<li>Not listed: →H fail rows for {{dropped_pipeline_models}} equal their plain rows; see Pipelines.</li>
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
<li>Token floor = text Codex's runner (its harness) adds before the task. This includes the system prompt and tool descriptions.</li>
<li>Bars show mean input per call, including the task.</li>
<li>Solid = served from cache. Faded = uncached.</li>
<li>Low-context rows use trimmed prompts. All these runs had tools off.</li>
<li><a href="#notation">See Notation.</a></li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">Best luna fix: luna-high-bare →H all (Haiku checks every answer). Here, bare means Codex's system prompt was trimmed. It passed {{r_luna_high_bare_haiku_review_all_k}} at {{r_luna_high_bare_haiku_review_all_upp}} per pass. Pipelines ran only on the {{n_rescue_problems}}-problem {{set_label}}.</p>
<div class="chart floor"><h3>Passes, $ per pass, median seconds</h3><p class="sub">{{pipes_caption}}</p>{{w_pipes}}</div>
<ul class="tight small">
<li>sol61-high and astra-medium never failed an example, so Haiku never ran.</li>
<li>Normal speed uses separate runs. ⚡ pipeline rows replay cached answers.</li>
<li>Low-context rows use trimmed prompts. <a href="#notation">See Notation.</a></li>
</ul>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>✅ CONCLUSION</h2>
<b>Use Codex first: on a subscription its calls cost {{claude_zero}} cash. Paying per call? Haiku is cheapest. Need speed? Sonnet.</b>
<p>Default route:</p>
<ol class="tight">
<li>Send the task to sol61-high ({{claude_zero}} on quota). {{default_route_scope}}</li>
<li>Run the worked examples.</li>
<li>If one fails, hand it to haiku-low.</li>
</ol>
<ul class="tight">
<li>Paying per call? haiku-low is cheapest at {{budget_pass}}+ passing. Choose haiku-high for no misses. For speed, pick sonnet-medium: {{sonnet_medium_med}} s against haiku-high's {{haiku_high_med}} s. It costs {{sm_vs_hh_x}} as much per pass. Avoid luna-low or luna-medium alone.</li>
<li>{{hb_conclusion_copy}}</li>
</ul>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<p class="small">Explorer plots any two measures. {{rung_breaks}}. luna-low-bare breaks at {{bare_rung_break}}; see the grid. Repo tasks all passed {{ag_k}}. Costs ranged from {{ag_luna_low_usd}} to {{ag_astra_medium_usd}}.</p>
<details><summary>🎛️ Explorer and more charts</summary>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:agentic.svg|Repo tasks: pass rate vs $ per run. All marks are circles here; read the labels}}
</details>

<p class="small"><a href="#notation">See Notation.</a></p>
</section>
<section class="notes" id="notes">
<h2><span class="num"></span>Notes: caveats, code quality, appendix</h2>
<p class="small">Small sample: read the intervals first. {{n_exploratory}} configs were added after the main run (†), including the winning sol61-high. Sonnet's code read worst in a blind review.</p>
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
<p class="small">Fast mode: same passes, {{fm_faster}} faster per call. Median times: {{fm_fast_s}} s vs {{fm_ctrl_s}} s. Price: {{fm_mult}} list. xhigh effort (above high): same passes, {{fm_x_cost}} the cost, slower.</p>
{{table:fastmode}}
<p class="small">The default-tier control is a separate {{fm_n}}-try run. Its {{fm_ctrl_s}} s differs from the Results row.</p>
<p class="small">The blind read covered {{bl_n}} solutions. A code-only reviewer would refuse to merge {{bl_blocks}}, all sonnet-medium. It scored {{bl_sonnet_score}}. Other configs scored {{bl_other_scores}} with none blocked.</p>
<p class="small">{{blind_caption}}</p>
{{table:blind}}
</details>
<details id="appendix"><summary>📎 Appendix</summary>
<p class="small">Headline numbers: see <a href="#method">How it was run</a>.</p>
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
<li>Two more luna-low variants are listed under Everything we tried. luna-low-noshell-B1 removes shell context and asks for edge cases first. luna-low-noshell-B2 also asks for a detailed reasoning summary. {{noshell_comparison}}</li>
<li>The recorded calls took about {{hb_minutes}} minutes of wall time.</li>
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
<li><b>L7: haiku-low has misses; sonnet-medium passed every try.</b><ul>
<li>Each problem had {{repeats}} tries.</li>
<li>Problems:<ul>{{l7_problem_items}}</ul></li>
<li>haiku-low passed {{l7_hl_k}}. It cost {{l7_haiku_low_upp}} per pass.</li>
<li>sonnet-medium passed {{l7_sm_k}}. It cost {{l7_sonnet_medium_upp}} per pass.</li>
</ul></li>
<li><b>Escalation: luna-high fixes most of luna-medium's misses.</b><ul>
<li>We reran weak problems at higher effort.</li>
<li>Problems:<ul>{{escalation_problem_items}}</ul></li>
<li>luna-high passed {{esc_k}}.</li>
<li>{{esc_vs}} had passed {{esc_base}}.</li>
</ul></li>
<li><b>Retry vs Haiku: luna-high-bare retries matched Haiku fixes.</b><ul>
<li>Haiku fixed failed examples; the pipeline passed {{r_luna_high_bare_haiku_on_fail_k}}.</li>
<li>It cost {{r_luna_high_bare_haiku_on_fail_upp}} per pass.</li>
<li>Same-model retries passed {{r_luna_high_bare_retry_on_fail_k}}.</li>
<li>They cost {{r_luna_high_bare_retry_on_fail_upp}} per pass.</li>
<li>These rows use the {{set_label}}, with {{rescue_n}} attempts each.</li>
</ul></li>
<li><b>Example checks miss some bad answers.</b><ul>
<li>A fresh luna-high-bare run had {{g_hi_bad}} bad answers.</li>
<li>Checks caught {{g_hi_fixed}}. Haiku fixed {{g_hi_fixed_words}}.</li>
<li>Checks missed {{g_hi_missed}}.</li>
<li>The run without checks had {{r_luna_high_bare_miss}} bad answers.</li>
</ul></li>
<li><b>Planning: Haiku plans cost more than Haiku checks.</b><ul>
<li>luna-low passed {{r_luna_low_k}} without a plan.</li>
<li>It passed {{r_haiku_low_plan_luna_low_k}} with a Haiku plan.</li>
<li>luna-high-bare passed {{r_luna_high_bare_k}} either way.</li>
<li>Both Haiku-plan pipelines cost more than Haiku checking after.</li>
</ul></li>
<li><b>Pilot: every config passed, so the pilot ranked nothing.</b><ul>
<li>The pilot used {{pilot_problems}} well-known LeetCode problems.</li>
</ul></li>
<li><b>Fast-mode pilot: sol61-low got faster; luna-low did not.</b><ul>
<li>The pilot used {{fast_problems}} problems across {{fast_rounds}} rounds.</li>
<li>It used {{fast_mult}} list price.</li>
<li>sol61-low fell from {{fast_sol_def}} s to {{fast_sol_fast}} s.</li>
<li>luna-low changed from {{fast_luna_def}} s to {{fast_luna_fast}} s.</li>
<li>This pilot supplies the only fast-mode data at low effort.</li>
</ul></li>
<li><b>Original repair run: we lost its prompt but reran committed code.</b><ul>
<li>The original luna-low → Haiku-fixes-all run passed {{r_luna_low_haiku_low_repair_k}}.</li>
<li>The rerun from committed code passed {{r_luna_low_haiku_review_all_k}}.</li>
<li>Both use the {{set_label}}, with {{rescue_n}} attempts per row.</li>
</ul></li>
<li><b>Repo tasks: every config passed every edit.</b><ul>
<li>Each config tackled {{n_tasks}} edits, {{agent_repeats}} times each, with tools.</li>
<li>Every config passed {{ag_k}}.</li>
<li>Costs per run:<ul>
<li>luna-low: {{ag_luna_low_usd}}.</li>
<li>haiku-low: {{ag_haiku_low_usd}}.</li>
<li>haiku-high: {{ag_haiku_high_usd}}.</li>
<li>sonnet-medium: {{ag_sonnet_medium_usd}}.</li>
<li>sol61-medium: {{ag_sol61_medium_usd}}.</li>
<li>sol61-high: {{ag_sol61_high_usd}}.</li>
<li>astra-medium: {{ag_astra_medium_usd}}.</li>
</ul></li>
</ul></li>
</ul>
</details>
{{w_everything}}
</section>
