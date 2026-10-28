<header class="head">
<p class="headlinks"><a href="https://chimericlabs.xyz/">← Chimeric Labs</a><a href="https://github.com/chimera-defi/dispatchbench">Source on GitHub</a></p>
<h1>DispatchBench: which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#pareto">Cost vs accuracy</a><a href="#results">Results</a><a href="#grok">Grok and Devin</a><a href="#method">How it was run</a><a href="#fail">Where they fail</a><a href="#tokens">Baseline input tokens</a><a href="#pipes">Pipelines</a><a href="#fair">Whose bench?</a><a href="#conclusion">Conclusion</a><a href="#limits">Limitations</a><a href="#extras">More charts</a><a href="#notes">Notes</a><a href="#interesting">Interesting</a><a href="#equiv">Codex vs Claude</a></nav>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>🏆 WINNER</h2>
<ul class="tight">
<li><b>{{winner_default}}</b></li>
<li><b>{{winner_budget}}</b></li>
<li><b>{{winner_speed}}</b></li>
<li>{{winner_claude_to_codex}}</li>
<li>{{winner_codex_to_claude}}</li>
</ul>
<p><b>{{winner_intro}}</b></p>
<details class="small"><summary>Picks and model names</summary>
<p>{{winner_price}}</p>
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
<p class="small">LeetCode-style problems, written fresh for this bench. {{run_dates}}</p>
</section>
<section id="pareto">
<h2><span class="num"></span>📊 Cost vs accuracy</h2>
<div class="chart"><h3>🎯 Pass rate vs $ per pass</h3>{{w_pass_cost}}</div>
<details open><summary>⏱️ Speed vs $ per pass</summary><div class="chart"><p class="sub">Best trade-offs, pass rate at least {{min_pass}}.</p>{{w_speed_cost}}</div></details>
<div class="legend"><span><span class="dot" style="background:var(--claude)"></span>Haiku</span><span><span class="dot" style="background:var(--sonnet)"></span>Sonnet</span><span><span class="dot" style="background:var(--codex)"></span>Codex</span><span><span class="dot" style="background:var(--grok);box-shadow:0 0 0 1.5px #fff"></span>Grok</span><span><span class="ring"></span>Best trade-off (ringed, numbered)</span></div>
<details class="small"><summary>How to read this data</summary>
<ul class="tight small">
<li>Colour = vendor. Shape = model: ● Haiku · ■ Sonnet. Triangles = luna · ◆ sol · ★ astra · ⬟ terra. Luna triangle direction = effort: up low, right medium, down high. Alternate Codex colour = the older gpt-{{older_generation}} models (luna56, sol56).</li>
</ul>
<h4>Speed and bare prompts</h4>
<ul class="tight small">
<li>Filled = normal speed. Hollow (⚡) = fast mode, joined by a thin line to its normal-speed point. Dashed edge = bare prompt.</li>
<li>luna-low-bare = luna-low with Codex's system prompt trimmed.</li>
</ul>
<h4>Points and labels</h4>
<ul class="tight small">
<li>Numbered points are named under each chart. Labels mark only the named picks. Hover or tap any point or key row for the rest. Ringed, numbered points are best trade-offs. Shading marks what they beat.</li>
<li>The {{ci_level}} range is shown as whiskers.</li>
</ul>
<h4>Key numbers</h4>
<ul class="tight small">
<li>haiku-high has a pass rate of {{haiku_high_pass}}, at {{haiku_high_upp}} per pass. sol61-high also has a pass rate of {{sol61_high_pass}}, at ~{{sol61_high_upp}} per pass. sol61-high costs {{claude_zero}} on Codex quota.</li>
<li>The cheapest luna configs cost less but miss about {{cheap_miss_words}}.</li>
<li>luna-low pass rate: {{luna_low_pass}}. luna-low-bare pass rate: {{luna_low_bare_pass}}. luna-medium pass rate: {{luna_medium_pass}}.</li>
</ul>
<h4>Sets and pipelines</h4>
<p class="set-note">{{w_rescue_subtitle}}</p>
{{w_sets}}
<p class="small">Pipelines are on the "{{set_label_title}} + pipelines" tab.</p>
</details>
</section>
<section id="results">
<h2><span class="num"></span>📋 Results</h2>
<p class="small">sol61-high ⚡ is the Codex pick. haiku-high is the cheapest config with no misses on the main ladder.</p>
<p class="small">Verdict key: {{verdict_key}}</p>
{{w_short_table}}
<details><summary>Full table: intervals and slow-call time</summary>
{{w_full_table}}
</details>
<div class="chart floor"><h3>⚡ Codex fast mode: seconds and $ per pass</h3>{{w_fast}}</div>
<details class="small"><summary>How to read this data</summary>
{{w_result_notes}}
<h4>Table columns</h4>
<ul class="tight small">
<li>Claude $ column: all = every dollar of that row went to Claude.</li>
<li>Pipeline rows show only the Haiku share.</li>
<li>Click a header to sort within a group. <a href="#notation">Symbols: see Notation.</a></li>
</ul>
<h4>Retest set</h4>
<ul class="tight small">
<li>{{set_label_title}} = the {{n_rescue_problems}} problems a cheap luna config missed. Its single-model rows reuse earlier attempts.</li>
<li>Not listed: →H fail rows for {{dropped_pipeline_models}}. Haiku never ran, so their results match the plain rows.</li>
</ul>
<h4>Pass rate and time</h4>
<ul class="tight small">
<li>Pass rate is pass@1: the share of single attempts that pass every hidden test.</li>
<li>Every pass rate names its rule. Function track: {{rule_function}}. Repo tasks use one headline rule, task complete: {{repo_legend}}. Counts read like "{{ag_k}}".</li>
<li>The {{ci_level}} range is the pass-rate uncertainty shown in the table.</li>
<li>Slow-call time: the time within which {{p90_percent}} of calls finished.</li>
<li>The lower end of the {{ci_level}} range is shown as ≥N% when all passed.</li>
</ul>
<ul class="tight small">
<li>Most configs ran {{n_calls}} calls ({{calls_exceptions_page}}). † = exploratory, added after seeing the main-run results.</li>
</ul>
<h4>Fast mode</h4>
<ul class="tight small">
<li>Pairs compare sol61-high and astra-medium at normal speed and ⚡.</li>
<li>The model and effort stay the same. The main ladder and L7 each passed every try.</li>
<li>Fast-mode $ uses {{fm_mult}} list price. This multiplier comes from the pricing page.</li>
</ul>
<h4>Codex $</h4>
<ul class="tight small">
<li>Codex $ is an estimate: tokens × list price, not a bill. ~ marks estimates.</li>
<li>On a subscription it uses quota instead. <a href="#notation">See Notation.</a></li>
</ul>
</details>
</section>
<section id="grok">
<h2><span class="num"></span>Grok and Devin</h2>
{{table:grok_lead}}
<h3>Where does Grok get to?</h3>
{{table:grok_full_reach}}
<p class="small">{{grok_full_note}}</p>
<h3>Closest lanes by pass rate</h3>
{{table:grok_full_closest}}
<details><summary>Every lane on the same problems</summary>
{{table:grok_full_lanes}}
</details>
<h3>Is Grok better at anything?</h3>
{{table:grok_better}}
<h3>{{grok_first_title}}</h3>
{{table:grok_summary}}
{{table:grok_at_glance}}
<h3>First run: where it got to</h3>
<p class="small">{{grok_key}}</p>
{{table:grok_reach}}
<p class="small">{{grok_reach_note}}</p>
<h3>First run: closest lanes</h3>
{{table:grok_equivalent}}
{{table:grok_selection_note}}
<details><summary>All comparable lanes</summary>
<p>{{grok_match_rule}}</p>
<p class="small">{{grok_scope}}</p>
{{table:grok_equivalent_all}}
</details>
<h3>First run: was Grok better at anything?</h3>
{{table:grok_verdict}}
{{table:grok_repository}}
<h3 id="devin">Devin on the free tier</h3>
<p>{{devin_lead}}</p>
{{table:devin_reach}}
<ul class="tight small">
<li>{{devin_why}}</li>
<li>{{devin_bypass}}</li>
<li>{{devin_stage2}}</li>
</ul>
<p><b>{{devin_verdict}}</b> The Results table and the failure grid list it as {{devin_group}}.</p>
{{w_grok_catalog}}
</section>
<section class="method" id="method">
<h2><span class="num"></span>❓ How it was run</h2>
<p class="small">Every config (model + effort) got the same new problems and hidden tests. Tools were off: no code runs, file reads or search. Logs confirm it for {{codex_tool_free}} Codex calls. {{terra_tool_note}}</p>
<details><summary>📚 Problems by rung (Easy/Medium/Hard)</summary>
<ul class="tight small">
<li>We wrote these problems for this bench.</li>
<li>Each LeetCode link is the closest analogue I found by hand.</li>
<li>Pilot links say "source": those problems come from LeetCode.</li>
<li>Rungs L1–L6 follow this bench's own difficulty order.</li>
<li>Rung and LeetCode difficulty can disagree:<ul>{{badge_disagreement_items}}</ul></li>
{{w_problems}}
</ul>
</details>
<ul class="tight small">
<li>Each config tries each problem {{repeats}} times, tools off.</li>
<li>Total spend, by kind: Claude {{claude_usd}} (CLI-reported), Codex {{codex_usd}} (list-price proxy), Grok {{grok_cli_usd}} (CLI-reported), plus Claude pilot and appendix arms {{claude_aux_usd}}.</li>
</ul>
<details><summary>📐 How to read this data: sets, tests, prices, intervals</summary>
<ul class="tight small">
<li>Planted wrong answers must fail the hidden tests. Sample tests = the worked examples the model sees.</li>
<li>Cost totals leave out the pilot, runner (harness) bias, trim and {{set_label}} pipeline runs.</li>
<li>Sets:<ul>
<li>{{main_set_label}} has {{n_problems}} problems. Each gets {{repeats}} tries. Total: {{n_calls}} calls per config that ran it in full.</li>
<li>{{l7_set_label}} has {{n_l7}} problems. Each gets {{repeats}} tries. Total: {{l7_n}} calls.</li>
<li>{{set_label_title}} covers the {{n_rescue_problems}} main-ladder problems. They are the ones that {{rescue_rule}}. They were chosen after the main run. Each config made {{rescue_n}} calls.</li>
<li>Repo tasks: {{n_tasks}} edits. Each gets {{agent_repeats}} tries. Total: {{ag_n}} calls.</li>
</ul></li>
<li>Hidden tests: fixed cases, random cases checked against a reference, and large cases for speed.</li>
<li>Claude $: what the CLI reports.</li>
<li>The {{ci_level}} range uses {{n_boot}} bootstrap resamples. It shows how much a rerun's pass rate can vary.</li>
<li>Run by Wren, a {{orchestrator}} orchestrator.</li>
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
<script type="application/json" id="data">__DATA__</script>
<p class="small">{{worst_failure}}.</p>
<details class="small"><summary>How to read this data</summary>
<ul class="tight small">
<li>Cells = passed/attempted. Green: all passed. Amber: more than half. Red: half or fewer.</li>
<li>Dash: not run. Scroll sideways for more configs.</li>
</ul>
</details>
<ul class="tight small">
<li>E/M/H = my LeetCode difficulty guess: Easy, Medium, Hard.</li>
</ul>
{{w_grid}}
<p class="small">{{grok_not_run}}</p>
<ul class="tight small">
<li>p04 taller_within (L2): luna-low, luna-medium and luna-low-bare each passed only {{p04_passes}} of {{repeats}} tries.</li>
<li>haiku-low never gave a wrong answer.</li>
<li>Its {{hl_main_misses}} main-ladder misses: {{hl_main_timeouts}} too slow. {{hl_main_crashes}} crash.</li>
<li>Its {{l7_hl_fail}} L7 misses: all too slow.</li>
</ul>
</section>
<section id="tokens">
<h2><span class="num"></span>🧱 Baseline input tokens per call</h2>
<p class="small">Trimming luna-low's Codex system prompt and tool features cuts mean input by {{in_cut}}.</p>
<div class="chart floor">{{w_floor}}</div>
<details class="small"><summary>How to read this data</summary>
<ul class="tight small">
<li>Baseline input tokens = text Codex's runner adds before the task. This includes the system prompt and tool descriptions.</li>
<li>Bars show mean input per call, including the task.</li>
<li><a href="#notation">See Notation.</a></li>
</ul>
</details>
</section>
<section id="pipes">
<h2><span class="num"></span>🔗 Pipelines: plan, check, fix</h2>
<p class="small">A pipeline chains steps. Usually a single model writes, then Haiku checks. The best, luna-high-bare →H all, passed {{r_luna_high_bare_haiku_review_all_k}}. It costs {{r_luna_high_bare_haiku_review_all_upp}} per pass. haiku-medium alone also passed every try. That pipeline cost {{hm_vs_pipe_x}} as much.</p>
<div class="chart floor"><h3>Pass rate, $ per pass, median seconds</h3><p class="sub">{{pipes_caption}}</p>{{w_pipes}}</div>
<details class="small"><summary>How to read this data</summary>
<h4>Gates</h4>
<ul class="tight small">
<li>→H fail: Haiku fixes an answer only if a sample test fails. →H all: Haiku checks every answer.</li>
<li>sol61-high and astra-medium never failed a sample test, so Haiku never ran.</li>
<li>luna-low failed sample tests more often: {{g_lo_fixed}} repairs, so the gate helped it more.</li>
</ul>
<h4>Scope</h4>
<ul class="tight small">
<li>Pipelines ran only on the {{set_label}}.</li>
<li>{{fast_pipeline_note}}</li>
<li>⚡ pipeline rows reuse cached ⚡ answers. Other pipeline rows are new calls.</li>
</ul>
<ul class="tight small">
<li>Router: per main-ladder problem, the cheapest config that passed tries {{router_fit}}. Router evaluation tries: {{router_held}}. The router passed {{router_k}}. That cost ~{{router_share}} of haiku-high's $ per pass.</li>
</ul>
<p class="small"><a href="#notation">See Notation.</a></p>
</details>
</section>
<section id="fair">
<h2><span class="num"></span>⚖️ Whose bench?</h2>
<p class="small"><b>Does a Codex-built bench favour Codex models? {{hb_answer}} haiku-low still led on both, so no pick changes.</b></p>
{{chart:harness_bias.svg|{{hb_n_problems}} hard problems, {{hb_repeats}} tries each}}
{{table:harness_strengths}}
<details class="small"><summary>How to read this data</summary>
<p class="small">Our one-shot runner (Claude's bench): a single answer per try, tools off.</p>
<p class="small">Codex CLI loop: runs code, retries (Codex's bench).</p>
<h4>The benches</h4>
<ul class="tight small">
<li>{{bench_authorship}}</li>
<li>Codex's bench: each model runs in its vendor's agent CLI, which runs code and retries.</li>
<li>luna-low ran in Codex CLI, haiku-low in Claude Code: each vendor's cheapest model.</li>
<li>sol61-high was skipped: every try already passed.</li>
</ul>
<h4>What changed</h4>
<ul class="tight small">
<li>luna-low went {{hb_luna_low_change}}. haiku-low went {{hb_haiku_low_change}}.</li>
<li>Running code cut luna-low's wrong outputs from {{hb_luna_wrong_one}} to {{hb_luna_wrong_agent}}. Crashes fell from {{hb_luna_crash_one}} to {{hb_luna_crash_agent}}.</li>
<li>{{hb_luna_cost}} {{hb_haiku_cost}} Overall, Codex's bench cost {{hb_total_x}} as much per pass.</li>
</ul>
<ul class="tight small">
<li>The gap moved {{hb_diff_points}} points, below our {{hb_bar_points}}-point bias threshold. Confidence level: {{ci_level}}. The range is {{hb_range_points}} points.</li>
</ul>
<ul class="tight small">
<li>Luna-low variants B1 and B2 are listed under Everything we tried. luna-low-noshell-B1 removes shell context and asks for edge cases first. luna-low-noshell-B2 also asks for a detailed reasoning summary. {{noshell_comparison}}</li>
</ul>

<p class="small">Time per pass = summed call seconds divided by passes.</p>
</details>
<details class="small"><summary>How Codex built its bench</summary>
<ul class="tight small">
<li>gpt-6.1-sol high designed and wrote it in five turns.</li>
<li>Its dry runs missed two sandbox bugs. A live call found them; Codex fixed both.</li>
<li>A final "plan and reorient" nudge changed no code.</li>
<li>{{hb_subset}}</li>
<li>We lifted its repeat cap, a two-line change, then ran {{hb_full_calls}} calls.</li>
<li>It finished with {{hb_errors}} runner errors and no timeouts, in about {{hb_minutes}} minutes.</li>
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
<li>If speed matters most, use sonnet-medium. It takes {{sonnet_medium_med}} s to haiku-high's {{haiku_high_med}} s. sonnet-medium costs {{sm_vs_hh_x}} as much per pass.</li>
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
<li>Most have a LeetCode analogue, and LeetCode code is widely public.</li>
<li>The problems ship with this repo, so later models can read them.</li>
<li>The {{ci_level}} range resamples whole problems, since tries on the same problem are related.</li>
<li>L7 has {{n_l7}} problems. Perfect score: {{l7_bound}}. That only shows a pass rate of at least {{l7_lo}}.</li>
<li>Repo tasks: luna-low completes {{ag_mark_luna_iso}} in the clean-home rerun and every other config completes every run. With {{ag_n}} tasks they cannot rule out skill differences.</li>
<li>Paired gaps of {{nosep_gap}} points or less showed no separation; {{sep_gap}}-point gaps did.</li>
<li><code>PLAN.md</code> was committed before the main run; a same-day pilot came first.</li>
<li>{{n_exploratory}} configs were added after seeing the main-run results (†). These include the haiku-high and sol61-high picks:<ul>{{exploratory_items}}</ul></li>
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
<li>Numbers come from <code>results/dataset.json</code>, which is built from the <code>results/*.jsonl</code> run files.</li>
</ul>
</details>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>🔍 More charts</h2>
<p class="small">{{rung_breaks}}. luna-low-bare breaks at {{bare_rung_break}}; see the grid.</p>
<p class="small">Repo tasks, task complete (hidden in brackets): luna-low {{ag_mark_luna_iso}} in the clean-home rerun ({{ag_mark_luna_orig}} in the original run); every other config completed every run. Every task prompt told agents to add tests and that all tests must pass. {{ag_why_red}} Costs ranged from {{ag_luna_low_usd}} to {{ag_astra_medium_usd}} per run; per complete task luna-low costs {{ag_luna_low_upp}} against haiku-low's {{ag_haiku_low_upp}}.</p>
<p class="small">{{t1v2_line}}</p>
{{table:t1_regrade}}
<p class="small"><b>Correction, 2026-10-28.</b> A reader pointed out that "passed every hidden test" hid luna-low's visible-test misses. The headline is now task complete, with the hidden-suite count beside it.</p>
<details><summary>🎛️ Explorer and more charts</summary>
<p class="small">Explorer plots any pair of measures.</p>
<div class="chart"><h3>🎛️ Explorer</h3>{{w_explorer}}</div>
{{chart:pass_by_rung.svg|Pass rate by difficulty rung}}
{{chart:agentic.svg|Repo tasks: task complete vs $ per run (filled: task complete; ring: hidden suite only). {{agentic_fast_caption}}}}
</details>

<p class="small"><a href="#notation">See Notation.</a></p>
</section>
<section class="notes" id="notes">
<h2><span class="num"></span>Notes: code quality, fast mode, appendix</h2>
<p class="small">Sonnet's code read worst in a blind review.</p>

<details><summary>🧪 Code quality</summary>
{{table:quality}}
<ul class="tight small">{{quality_fast_items}}</ul>

</details>
<details><summary>⚡ Codex fast mode and xhigh</summary>
<p class="small">On the {{set_label}}, fast mode kept every pass and was {{fm_faster}} faster. Median times: {{fm_fast_s}} s vs {{fm_ctrl_s}} s. Price: {{fm_mult}} list, not a measured bill. xhigh effort (above high): same passes, {{fm_x_cost}} the cost, slower, no better code.</p>
{{table:fastmode}}

<p class="small">The blind read covered {{bl_n}} solutions. A code-only reviewer would refuse to merge {{bl_blocks}}, all sonnet-medium. It scored {{bl_sonnet_score}}. Other configs scored {{bl_other_scores}} with none blocked. One reviewer and one solution per cell: a sign of bad code, not a ranking.</p>
<p class="small">{{blind_caption}}</p>
{{table:blind}}
</details>
<details class="small"><summary>How to read this data</summary>
<h4>Code quality columns</h4>
<ul class="tight small">
<li>Complexity = cyclomatic complexity (branch count) of the most complex function, via radon.</li>
<li>Lint = ruff style warnings per solution.</li>
<li>Worse growth = time-growth exponent more than {{growth_margin}} above the reference's.</li>
<li>Time vs ref = run time divided by the reference solution's.</li>
<li>Mem vs ref = memory divided by the reference solution's.</li>
<li>Below {{ref_unit}} is faster or leaner.</li>
</ul>
<h4>Code quality scope</h4>
<ul class="tight small">
<li>Scored: main-ladder passing solutions, {{q_rows}} rows.</li>
<li>All {{n_solutions}} solutions are in <code>results/solutions</code>.</li>
<li>On {{q_worst_problem}}, {{q_slow_n}} solutions run slower than the reference. Slower means at least {{q_slow_bar}} longer. The smallest slowdown is {{q_slow_lo}}. They come from {{q_slow_cfgs}} configs. The worst is a {{q_worst_cfg}} solution at {{q_worst_x}}.</li>
</ul>
<h4>Fast-mode control</h4>
<p class="small">The default-tier control is a separate {{fm_n}}-try run. Its {{fm_ctrl_s}} s differs from the Results row.</p>
</details>
<details id="appendix"><summary>📎 Appendix</summary>
<p class="small">Headline numbers: see <a href="#method">How it was run</a>.</p>
<h3>Codex CLI in the main benchmark</h3>
<ul class="tight small">
<li>Codex also answered through its own CLI in the main benchmark.</li>
<li>We ignored personal settings and disabled tools.</li>
<li>The <code>luna-*-bare</code> rows test how much Codex's system prompt and tool text matter.</li>
</ul>
<p class="small">Repo-task rows were rerun with a clean Codex home.</p>
<p class="small">A clean rerun checked {{isolation_calls_matched}} other calls.</p>
<p class="small">It passed {{isolation_passes_isolated}} versus {{isolation_passes_original}} originally, so those rows were kept.</p>
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
<li>{{int_terra}}</li>
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
<p><b>{{equiv_takeaway}}</b></p>
{{table:equiv_all}}
<details><summary>📝 How to read this data: matches</summary>
<ul class="tight small">
<li>Match = the cheapest other-vendor config passing at least as often.</li>
<li>{{equiv_fastest}}</li>
<li>{{equiv_near}}</li>
<li>All rows use the main ladder.</li>
</ul>
</details>
</section>
