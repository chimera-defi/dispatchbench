<header class="head">
<h1>DispatchBench: which model should a coding task go to?</h1>
<p class="small">LeetCode-style problems, written fresh for this bench. {{run_dates}}</p>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#pareto">Cost vs accuracy</a><a href="#results">Results</a><a href="#method">How it was run</a><a href="#fail">Where they fail</a><a href="#tokens">Token floor</a><a href="#pipes">Pipelines</a><a href="#fair">Whose bench?</a><a href="#conclusion">Conclusion</a><a href="#limits">Limitations</a><a href="#extras">More charts</a><a href="#notes">Notes</a><a href="#interesting">Interesting</a><a href="#equiv">Codex vs Claude</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<p><b>{{winner_intro}}</b></p>
<details class="small"><summary>Picks and model names</summary>
<p>{{winner_price}}</p>
<p class="small">{{winner_fallback}}</p>
<p class="small">Against haiku-high, sol61-high takes {{s61h_hh_t}} the time and ~{{s61h_hh_c}} the $ per pass. ⚡ makes that {{s61f_hh_t}} the time at ~{{s61f_hh_c}} the $.</p>
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
</details>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="ring"></span>Best trade-off (ringed, numbered)</span></div>
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
<details open><summary>⏱️ Speed vs $ per pass</summary><div class="chart"><p class="sub">Best trade-offs among configs passing at least {{min_pass}}.</p>{{w_speed_cost}}</div></details>
<details class="small"><summary>How to read these charts</summary>
<p class="small">haiku-high passes {{haiku_high_pass}} at {{haiku_high_upp}} per pass. sol61-high also passes {{sol61_high_pass}} at ~{{sol61_high_upp}} per pass. It costs {{claude_zero}} on Codex quota. The three cheapest luna configs cost less but miss about {{cheap_miss_words}}.</p>
<p class="set-note">{{w_rescue_subtitle}}</p>
{{w_sets}}
<ul class="tight small">
<li>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet. Triangles = luna · ◆ sol · ★ astra. Luna triangle direction = effort: up low, right medium, down high. Alternate Codex colour = the older gpt-{{older_generation}} models (luna56, sol56).</li>
<li>Filled = normal speed. Hollow (⚡) = fast mode, joined by a thin line to its normal-speed point. Dashed edge = bare prompt.</li>
<li>Numbered points are named under each chart. Labels mark only the named picks. Hover or tap any point or key row for the rest.</li>
<li>Ringed, numbered points are best trade-offs. Shading marks what they beat.</li>
<li>Whiskers: {{ci_level}} confidence interval (bootstrap).</li>
<li>luna-low {{luna_low_pass}}. luna-low-bare {{luna_low_bare_pass}}. luna-medium {{luna_medium_pass}}.</li>
<li>luna-low-bare = luna-low with Codex's system prompt trimmed.</li>
<li>Pipelines are on the "{{set_label_title}} + pipelines" tab.</li>
</ul>
</details>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
<p class="small">sol61-high ⚡ is the Codex pick. haiku-high is the cheapest config with no misses on the main ladder.</p>
<p class="small">Verdict key: {{verdict_key}}</p>
{{w_short_table}}
<ul class="tight small">
<li>Claude $ column: all = every dollar of that row went to Claude.</li>
<li>Pipeline rows show only the Haiku share.</li>
<li>Click a header to sort within a group. <a href="#notation">Symbols: see Notation.</a></li>
<li>{{set_label_title}} = the {{n_rescue_problems}} problems a cheap luna config missed. Its single-model rows reuse earlier attempts.</li>
<li>Not listed: →H fail rows for {{dropped_pipeline_models}}. Haiku never ran, so they pass like their plain rows.</li>
</ul>
<details><summary>Full table: intervals and p90</summary>
<p class="small">Intervals show pass-rate uncertainty. p90 covers slower calls.</p>
{{w_full_table}}
<ul class="tight small">
<li>Each config ran {{n_calls}} calls. † = exploratory, added after seeing the main-run results.</li>
<li>pass@1 is the fraction of individual attempts passing all hidden tests.</li>
<li>p90 = time within which {{p90_percent}} of calls finished.</li>
<li>≥N% (all passed) = lower {{ci_level}} bound over the problems, when nothing failed.</li>
</ul>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3>{{w_fast}}</div>
<ul class="tight small">
<li>Pairs compare sol61-high and astra-medium at normal speed and ⚡.</li>
<li>The model and effort stay the same. Both the main ladder and L7 passed everything.</li>
<li>Fast-mode $ uses {{fm_mult}} list price. This multiplier comes from the pricing page.</li>
<li><a href="#notation">Codex $ is an estimate: see Notation.</a></li>
</ul>
</details>
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Every config (model + effort) got the same new problems and hidden tests. Tools were off: no code runs, file reads or search. Logs confirm it for {{codex_tool_free}} Codex calls.</p>
<details><summary>📚 Problems by rung (Easy/Medium/Hard)</summary>
<ul class="tight small">
<li>We wrote these problems for this bench.</li>
<li>Each LeetCode link is the closest analogue I found by hand.</li>
<li>Pilot links say "source": those problems come from LeetCode.</li>
<li>Easy/Medium/Hard is my guess at LeetCode difficulty.</li>
<li>Rungs L1–L6 follow this bench's own difficulty order.</li>
<li>The two can disagree:<ul>{{badge_disagreement_items}}</ul></li>
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>Pass = every hidden test passes. Planted wrong answers must fail them. Sample tests = the worked examples the model sees.</li>
<li>The bench cost {{claude_usd}} on Claude. Codex quota use is estimated at {{codex_usd}}.</li>
</ul>
<details><summary>📐 Sets, tests, prices and intervals</summary>
<ul class="tight small">
<li>Cost totals leave out the pilot, harness-bias, trim and {{set_label}} pipeline runs.</li>
<li>Sets:<ul>
<li>{{main_set_label}}: {{n_problems}} problems, {{repeats}} tries each. Total: {{n_calls}} calls.</li>
<li>{{l7_set_label}}: {{n_l7}} problems, {{repeats}} tries each. Total: {{l7_n}} calls.</li>
<li>{{set_label_title}}: the {{n_rescue_problems}} main-ladder problems {{rescue_rule}}, chosen after the main run. Each config made {{rescue_n}} calls.</li>
<li>Repo tasks: {{n_tasks}} edits, {{agent_repeats}} tries each. Total: {{ag_n}} calls.</li>
</ul></li>
<li>Hidden tests: fixed cases, random cases checked against a reference, and large cases for speed.</li>
<li>Claude $: what the CLI reports.</li>
<li>Codex $: tokens × list price. ~ marks estimates, not bills.</li>
<li>{{ci_level}} intervals from {{n_boot}} bootstrap resamples: how much a rerun's pass rate could vary.</li>
<li>Run by Wren, a {{orchestrator}} orchestrator. It is not one of the configs tested.</li>
</ul>
</details>
<details><summary>🧩 Models and versions</summary>
<ul class="tight small">
<li>{{versions_claude}}</li>
<li>{{versions_codex}}</li>
<li>{{versions_extra}}</li>
</ul>
</details>
{{w_legend}}
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
<section id="tokens">
<h2><span class="num"></span>🧱 Token floor: input tokens per call</h2>
<p class="small">Trimming luna-low's Codex system prompt and tool features cuts mean input by {{in_cut}}.</p>
<div class="chart floor">{{w_floor}}</div>
<ul class="tight small">
<li>Token floor = text Codex's runner (its harness) adds before the task. This includes the system prompt and tool descriptions.</li>
<li>Bars show mean input per call, including the task.</li>
<li>All these runs had tools off.</li>
<li><a href="#notation">See Notation.</a></li>
</ul>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">A pipeline chains two steps. Usually one model writes, then Haiku checks. The best, luna-high-bare →H all, passed {{r_luna_high_bare_haiku_review_all_k}} at {{r_luna_high_bare_haiku_review_all_upp}} per pass. haiku-medium alone also passed every try; that pipeline cost {{hm_vs_pipe_x}} as much.</p>
<div class="chart floor"><h3>Passes, $ per pass, median seconds</h3><p class="sub">{{pipes_caption}}</p>{{w_pipes}}</div>
<ul class="tight small">
<li>Pipelines ran only on the {{set_label}}.</li>
<li>→H fail: Haiku fixes an answer only if a sample test fails. →H all: Haiku checks every answer.</li>
<li>bare = Codex's system prompt trimmed.</li>
<li>sol61-high and astra-medium never failed a sample test, so Haiku never ran.</li>
<li>{{fast_pipeline_note}}</li>
<li>luna-low failed sample tests more often: {{g_lo_fixed}} repairs, so the gate helped it more.</li>
<li>⚡ pipeline rows reuse cached ⚡ answers. Other pipeline rows are new calls.</li>
<li>Router: per main-ladder problem, the cheapest config that passed tries {{router_fit}}.</li>
<li>On tries {{router_held}} it passed {{router_k}}.</li>
<li>That cost ~{{router_share}} of haiku-high's $ per pass.</li>
<li><a href="#notation">See Notation.</a></li>
</ul>
</section>
<section id="fair">
<h2><span class="num"></span>⚖️ Claude's bench vs Codex's bench</h2>
<p class="small"><b>Does a Codex-built bench favour Codex models? {{hb_answer}} haiku-low still led on both, so no pick changes.</b></p>
{{chart:harness_bias.svg|{{hb_n_problems}} hard problems, {{hb_repeats}} tries each}}
<details class="small"><summary>What we tested and what we found</summary>
<ul class="tight small">
<li>{{bench_authorship}}</li>
<li>Claude's bench: one answer per try, tools off.</li>
<li>Codex's bench: each model runs in its vendor's agent CLI, which runs code and retries.</li>
<li>luna-low ran in Codex CLI, haiku-low in Claude Code: each vendor's cheapest model.</li>
<li>sol61-high was skipped: it already passed every try.</li>
<li>luna-low went {{hb_luna_low_change}}. haiku-low went {{hb_haiku_low_change}}.</li>
<li>Running code cut luna-low's wrong outputs from {{hb_luna_wrong_one}} to {{hb_luna_wrong_agent}}. Crashes fell from {{hb_luna_crash_one}} to {{hb_luna_crash_agent}}.</li>
<li>{{hb_luna_cost}} {{hb_haiku_cost}} Overall, Codex's bench cost {{hb_total_x}} as much.</li>
<li>Running code, not who built the bench, may explain the gain.</li>
<li>The gap moved {{hb_diff_points}} points, below our {{hb_bar_points}}-point bias bar.</li>
<li>The range is {{hb_range_points}} points, so a larger bias is possible. Confidence: {{ci_level}}.</li>
<li>Two more luna-low variants are listed under Everything we tried. luna-low-noshell-B1 removes shell context and asks for edge cases first. luna-low-noshell-B2 also asks for a detailed reasoning summary. {{noshell_comparison}}</li>
</ul>
{{table:harness_strengths}}
</details>
<details class="small"><summary>How Codex built its bench</summary>
<ul class="tight small">
<li>gpt-6.1-sol high designed and wrote it in five turns.</li>
<li>Its dry runs missed two sandbox bugs. A live call found them; Codex fixed both.</li>
<li>A final "plan and reorient" nudge changed no code.</li>
<li>{{hb_subset}}</li>
<li>We lifted its repeat cap, a two-line change, then ran {{hb_full_calls}} calls.</li>
<li>It finished with {{hb_errors}} harness errors and no timeouts, in about {{hb_minutes}} minutes.</li>
</ul>
</details>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>✅ CONCLUSION</h2>
<b>{{winner_line}}</b>
<ol class="tight">
<li>With Codex quota left, send each task to sol61-high ⚡.</li>
<li>Then run the sample tests. If one fails, haiku-low fixes it. {{default_route_scope}}</li>
<li>With Codex quota gone, use haiku-high. It is the cheapest config with no misses.</li>
</ol>
<ul class="tight">
<li>If speed matters most, use sonnet-medium. It takes {{sonnet_medium_med}} s to haiku-high's {{haiku_high_med}} s.</li>
<li>sonnet-medium costs {{sm_vs_hh_x}} as much per pass.</li>
<li>Don't use luna-low or luna-medium alone: they miss about {{cheap_miss_words}}.</li>
<li>{{hb_conclusion_copy}}</li>
</ul>
</section>
<section id="limits">
<h2><span class="num"></span>⚠️ Limitations</h2>
<p class="small"><b>A routing signal from a small, self-written set, not a general ranking. Read the intervals first.</b></p>
<details><summary>What could mislead</summary>
<ul class="tight">
<li>Scope: {{n_problems}} main problems, written for this bench.</li>
<li>Codex-as-orchestrator run: {{codex_orchestrator_status}}.</li>
<li>Most have a LeetCode analogue, so models may have seen similar code.</li>
<li>The problems ship with this repo, so later models may train on them.</li>
<li>Intervals resample whole problems, since tries on one problem are related.</li>
<li>L7 has {{n_l7}} problems. A perfect {{l7_bound}} there only shows a pass rate of at least {{l7_lo}}.</li>
<li>Every repo task passed, so they rank cost and speed, not skill.</li>
<li>Paired gaps of {{nosep_gap}} points or less did not separate; {{sep_gap}}-point gaps did.</li>
<li><code>PLAN.md</code> was committed before the main run; a same-day pilot came first.</li>
<li>{{n_exploratory}} configs were added after seeing the main-run results (†), including the haiku-high and sol61-high picks:<ul>{{exploratory_items}}</ul></li>
<li>A Codex call's estimated $ drops up to {{cache_swing}} when the prompt cache hits.</li>
<li>Latency is CLI wall clock.</li>
<li>We ran up to {{lanes}} calls at once on one host.</li>
<li>One run in time; hosted models change.</li>
<li>Codex needed our help to build its bench: <a href="#fair">see Whose bench?</a></li>
</ul>
</details>
<details><summary>Reproduce</summary>
<ul class="tight small">
<li>{{cite}}</li>
<li>Code, problems and raw results: <a href="https://github.com/chimera-defi/dispatchbench">dispatchbench on GitHub</a>, MIT licence.</li>
<li>Every number on this page comes from <code>results/dataset.json</code>.</li>
</ul>
</details>
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
<h2><span class="num"></span>Notes: code quality, fast mode, appendix</h2>
<p class="small">Sonnet's code read worst in a blind review.</p>
<details><summary>🧪 Code quality</summary>
{{table:quality}}
<ul class="tight small">{{quality_fast_items}}</ul>
<ul class="tight small">
<li>Complexity = cyclomatic complexity (branch count) of the most complex function, via radon.</li>
<li>Lint = ruff style warnings per solution.</li>
<li>Worse growth = time-growth exponent more than {{growth_margin}} above the reference's.</li>
<li>Time vs ref = run time divided by the reference solution's.</li>
<li>Mem vs ref = memory divided by the reference solution's.</li>
<li>Below {{ref_unit}} is faster or leaner.</li>
</ul>
<ul class="tight">
<li>Scored: main-ladder passing solutions, {{q_rows}} rows.</li>
<li>All {{n_solutions}} solutions are in <code>results/solutions</code>.</li>
<li>On {{q_worst_problem}}, {{q_slow_n}} solutions run at least {{q_slow_bar}} slower than the reference.</li>
<li>The smallest slowdown is {{q_slow_lo}}.</li>
<li>They come from {{q_slow_cfgs}} configs.</li>
<li>The worst is one {{q_worst_cfg}} solution at {{q_worst_x}}.</li>
</ul>
</details>
<details><summary>⚡ Codex fast mode and xhigh</summary>
<p class="small">On the {{set_label}}, fast mode kept every pass and was {{fm_faster}} faster. Median times: {{fm_fast_s}} s vs {{fm_ctrl_s}} s. Price: {{fm_mult}} list, not a measured bill. xhigh effort (above high): same passes, {{fm_x_cost}} the cost, slower, no better code.</p>
{{table:fastmode}}
<p class="small">The default-tier control is a separate {{fm_n}}-try run. Its {{fm_ctrl_s}} s differs from the Results row.</p>
<p class="small">The blind read covered {{bl_n}} solutions. A code-only reviewer would refuse to merge {{bl_blocks}}, all sonnet-medium. It scored {{bl_sonnet_score}}. Other configs scored {{bl_other_scores}} with none blocked.</p>
<p class="small">{{blind_caption}}</p>
{{table:blind}}
</details>
<details id="appendix"><summary>📎 Appendix</summary>
<p class="small">Headline numbers: see <a href="#method">How it was run</a>.</p>
<h3>Codex CLI in the main benchmark</h3>
<ul class="tight small">
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
<li>Haiku fixed failed sample tests; the pipeline passed {{r_luna_high_bare_haiku_on_fail_k}}.</li>
<li>It cost {{r_luna_high_bare_haiku_on_fail_upp}} per pass.</li>
<li>Same-model retries passed {{r_luna_high_bare_retry_on_fail_k}}.</li>
<li>They cost {{r_luna_high_bare_retry_on_fail_upp}} per pass.</li>
<li>These rows use the {{set_label}}, with {{rescue_n}} attempts each.</li>
</ul></li>
<li><b>Sample tests miss some bad answers.</b><ul>
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
<li>luna-low {{fast_luna_change}}.</li>
<li>This pilot supplies the only fast-mode data at low effort.</li>
</ul></li>
<li><b>Original repair run: we lost its prompt but reran committed code.</b><ul>
<li>The original luna-low → Haiku-fixes-all run passed {{r_luna_low_haiku_low_repair_k}}.</li>
<li>The rerun from committed code passed {{r_luna_low_haiku_review_all_k}}.</li>
<li>Both use the {{set_label}}, with {{rescue_n}} attempts per row.</li>
</ul></li>
</ul>
</details>
{{w_everything}}
</section>
<section id="interesting">
<h2><span class="num"></span>💡 Interesting findings</h2>
<ul class="tight">
<li>{{int_sol}}</li>
<li>{{int_luna}}</li>
<li>{{int_semi}}</li>
<li>{{int_harness}}</li>
<li>{{int_build}}</li>
<li>{{int_l7}}</li>
<li>{{int_trim}}</li>
<li>{{int_repo}}</li>
</ul>
</section>
<section id="equiv">
<h2><span class="num"></span>🔁 Codex vs Claude</h2>
<p><b>{{equiv_back_takeaway}}</b></p>
{{table:equiv_back}}
<p><b>{{equiv_takeaway}}</b></p>
<details><summary>📝 Claude → Codex table, how we matched</summary>
{{table:equiv}}
<ul class="tight small">
<li>Match = the cheapest Codex config that passes at least as often.</li>
<li>{{equiv_fastest}}</li>
<li>{{equiv_near}}</li>
<li>Codex $ is estimated from tokens at list price. On a subscription it uses quota instead.</li>
<li>All rows use the main ladder.</li>
</ul>
</details>
</section>
