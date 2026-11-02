<header class="head">
<h1>DispatchBench: which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#pareto">Cost vs accuracy</a><a href="#results">Results</a><a href="#problems">Problems</a><a href="#grok">Grok and Devin</a><a href="#method">Method</a><a href="#fail">Failures</a><a href="#tokens">Input tokens</a><a href="#pipes">Pipelines</a><a href="#fair">Whose bench?</a><a href="#limits">Limitations</a><a href="#extras">Other measures</a><a href="#notes">Notes</a><a href="#equiv">Codex vs Claude</a></nav>
<p class="small"><a href="#conclusion">Conclusion</a> · <a href="#interesting">Interesting findings</a></p>
</header>
<section class="verdict" id="winner">
<h2 class="eyebrow"><span class="num"></span>WINNER</h2>
<p class="winner-decision"><b>{{winner_default}}</b></p>
<ul class="tight">
<li>{{winner_budget}}</li>
<li>{{winner_speed}}</li>
<li>{{winner_checks}}</li>
</ul>
<p class="small muted">{{winner_claude_to_codex}}</p>
<p class="small muted">{{winner_codex_to_claude}}</p>
<details class="small"><summary>Picks and model names</summary>
<p>{{winner_intro}}</p>
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
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Against haiku-high, sol61-high costs more and runs slower, even with fast mode.</li>
</ul>
</details>
</section>
<section id="pareto">
<h2><span class="num"></span>Cost vs accuracy</h2>
{{w_explorer}}
<details class="small"><summary>Key numbers</summary>
<ul class="tight small">
<li>The cheapest luna configs cost less but miss about {{cheap_miss_words}}.</li>
</ul>
</details>
</section>
<section id="results">
<h2><span class="num"></span>Results</h2>
<p class="small">Verdicts: {{verdict_key}}</p>
{{w_short_table}}
<details><summary>Intervals and slow-call time</summary>
{{w_full_table}}
</details>
<div class="chart floor"><h3>Codex fast mode</h3>{{w_fast}}</div>
<details><summary>Reading the tables</summary>
<ul class="tight small">
<li>Pass rate: single attempts passing every hidden function test.</li>
<li>Repo tasks require task completion, including visible and hidden tests.</li>
<li>Slow-call time: {{p90_percent}} of calls finished within this time.</li>
<li>{{ci_level}} intervals resample whole problems.</li>
<li>† marks configs added after seeing results.</li>
<li>Claude $ counts only Claude's share; pipeline rows split costs.</li>
<li>Codex prices estimate tokens at list rates; subscriptions consume quota.</li>
<li>Fast-mode estimates use {{fm_mult}} list price.</li>
<li>Sort headers within each group. <a href="#notation">Symbols: Notation.</a></li>
</ul>
<h4>Retest set</h4>
<ul class="tight small">
<li>{{set_label_title}} = the {{n_rescue_problems}} problems a cheap luna config missed. Its single-model rows reuse earlier attempts.</li>
</ul>
<h4>Fast mode</h4>
<ul class="tight small">
<li>The model and effort stay the same. The main ladder and L7 each passed every try. This refers to sol61-high ⚡ and astra-medium ⚡; later terra61 priority results include misses.</li>
<li>Fast mode was not tried. Later priority results did try it; the earlier Terra run did not.</li>
</ul>
{{w_result_notes}}
</details>
<ul class="tight small">
<li>Retest single-model rows reuse earlier attempts on problems cheap luna configs missed.</li>
<li>Fast mode keeps model and effort; sol61-high ⚡ and astra-medium ⚡ kept their perfect main-ladder and harder-set scores.</li>
</ul>
</section>
<section id="problems">
<h2><span class="num"></span>Problems: try them yourself</h2>
<p class="small">Fresh problems, ordered by this bench's difficulty rungs.</p>
<p class="small">LeetCode links show analogues; E/M/H badges show our difficulty guesses.</p>
<ul class="tight small">{{w_problems}}</ul>
<ul class="tight small">
<li>Pilot links say "source": those problems come from LeetCode.</li>
<li>Rung and LeetCode difficulty can disagree:<ul>{{badge_disagreement_items}}</ul></li>
</ul>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Difficulty badges are estimates and can disagree with LeetCode's labels.</li>
</ul>
</details>
</section>
<section id="grok">
<h2 id="grok-and-devin"><span class="num"></span>Grok and Devin</h2>
{{w_grok_summary}}
<details class="small"><summary>Grok comparisons and methods</summary>
{{table:grok_lead}}
<h3>Closest lanes by pass rate</h3>
{{table:grok_full_closest}}
<p class="small">{{grok_full_note}}</p>
<h3>Is Grok better at anything?</h3>
{{table:grok_better}}
<h3>{{grok_first_title}}</h3>
{{table:grok_summary}}
{{table:grok_at_glance}}
<h3>First run: where it got to</h3>
<p class="small">{{grok_key}}</p>
<p class="small">{{grok_reach_note}}</p>
<h3>First run: closest lanes</h3>
{{table:grok_equivalent}}
{{table:grok_selection_note}}
<p>{{grok_match_rule}}</p>
<p class="small">{{grok_scope}}</p>
{{table:grok_verdict}}
{{table:grok_repository}}
</details>
<h3 id="devin">Devin on the free tier</h3>
<p>{{devin_lead}}</p>
<ul class="tight small">
<li>{{devin_why}}</li>
<li>{{devin_bypass}}</li>
<li>{{devin_stage2}}</li>
</ul>
<details><summary>Everything we tried</summary>
{{table:grok_catalog}}
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Devin missed the {{devin_stage2_min}}-pass continuation threshold, so additional repeats stopped.</li>
<li>Devin passed {{devin_k}} of {{devin_n}} problems, with timeouts, wrong answers, and a crash.</li>
<li>Grok's catalog covers low, medium, high, and fast-low efforts; medium has partial coverage.</li>
<li>Grok's closest matches, haiku-low and older Luna configs, run faster and cost less.</li>
<li>Isolated Devin CLI calls bypassed wrapper context, caching, fallback, and fixed model selection.</li>
<li>On repo tasks, grok47-low undercuts astra-medium and outruns sol61-high; Claude remains faster and cheaper.</li>
<li>Only {{devin_model}} runs free; other Devin-native models require Pro.</li>
</ul>
</details>
</section>
<h3 id="hetzner">Hetzner free tier</h3>
<p class="small"><a href="{{hetzner_endpoint}}">{{hetzner_endpoint}}</a> (OpenAI-compatible). {{hetzner_lead}} {{hetzner_gateway_note}} {{hetzner_scope}} {{hetzner_verdict}}</p>
{{table:hetzner_summary}}
<section class="method" id="method">
<h2><span class="num"></span>How it was run</h2>
<ul class="tight small">
<li>Each config receives identical problems and hidden tests; tool settings disable tool use.</li>
<li>Terra's logs cannot rule out tool use.</li>
<li>Main ladder: {{n_problems}} problems, {{repeats}} tries each.</li>
<li>L7: {{n_l7}} harder problems, scored separately.</li>
<li>{{set_label_title}}: {{n_rescue_problems}} problems cheap luna configs missed.</li>
<li>Repo tasks: {{n_tasks}} edits, {{agent_repeats}} tries each.</li>
<li>Hidden tests combine fixed cases, random reference checks, and large inputs.</li>
<li>Spend includes auxiliary runs; costs use each vendor's stated kind.</li>
<li>Claude: {{claude_total_usd}} CLI-reported.</li>
<li>Codex: {{codex_total_usd}} estimated at list price.</li>
<li>Grok: {{grok_cli_usd}} CLI-reported.</li>
</ul>
<details><summary>Models and versions</summary>
<ul class="tight small"><li>{{versions_claude}}</li><li>{{versions_codex}}</li><li>{{versions_extra}}</li></ul>
</details>
{{w_legend}}
<details class="small"><summary>How to read this data: sets, tests, prices, intervals</summary>
<p class="small">Every config (model + effort) got the same new problems and hidden tests. Tools were off: no code runs, file reads or search. Logs confirm it for {{codex_tool_free}} Codex calls. {{terra_tool_note}}</p>
<ul class="tight small">
<li>Total spend, by kind: Claude {{claude_total_usd}} (CLI-reported), Codex {{codex_total_usd}} (list-price proxy), Grok {{grok_cli_usd}} (CLI-reported). Includes pilot and appendix arms: Claude {{claude_aux_usd}}, Codex {{codex_aux_usd}} ({{codex_pilot_usd}} pilot, {{codex_appendix_usd}} appendix and trim).</li>
<li>Planted wrong answers must fail the hidden tests. Sample tests = the worked examples the model sees.</li>
<li>Cost totals leave out the pilot, runner (harness) bias, trim and {{set_label}} pipeline runs.</li>
<li>{{set_label_title}} covers the {{n_rescue_problems}} main-ladder problems. They are the ones that {{rescue_rule}}. They were chosen after the main run. Each config made {{rescue_n}} calls.</li>
<li>The {{ci_level}} range uses {{n_boot}} bootstrap resamples. It shows how much a rerun's pass rate can vary.</li>
<li>Run by Wren, a {{orchestrator}} orchestrator.</li>
</ul>
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Auxiliary spend: Claude {{claude_aux_usd}}, Codex {{codex_aux_usd}}, covering pilot, appendix, and trim runs.</li>
<li>Hidden tests reject planted wrong answers; sample tests are the examples shown to models.</li>
<li>Intervals use {{n_boot}} bootstrap resamples to estimate rerun variation.</li>
<li>Logs confirmed {{codex_tool_free}} tool-free Codex calls; Terra's item types remain uncertain.</li>
<li>Retest configs made {{rescue_n}} calls each, using problems selected after cheap luna misses.</li>
<li>Wren, a {{orchestrator}} orchestrator, ran the benchmark.</li>
</ul>
</details>
</section>
<section id="fail">
<h2><span class="num"></span>Where they fail</h2>
<script type="application/json" id="data">__DATA__</script>
<p class="small">{{worst_failure}}.</p>
<p class="small">Cells show passed/attempted; dashes mean untested. Scroll sideways for more configs.</p>
{{w_grid}}
<ul class="tight small">
<li>p04 taller_within (L2): luna-low, luna-medium and luna-low-bare each passed only {{p04_passes}} of {{repeats}} tries.</li>
<li>haiku-low never gave a wrong answer.</li>
<li>Main-ladder misses: {{hl_main_timeouts}} timeouts and {{hl_main_crashes}} crash.</li>
<li>Its {{l7_hl_fail}} L7 misses were timeouts.</li>
</ul>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>On taller_within, luna-low, luna-medium, and luna-low-bare each passed {{p04_passes}} of {{repeats}} attempts.</li>
</ul>
</details>
</section>
<section id="tokens">
<h2><span class="num"></span>Baseline input tokens</h2>
<p class="small">Trimming luna-low's system prompt cuts mean input by {{in_cut}}.</p>
<div class="chart floor">{{w_floor}}</div>
<p class="small">Bars include task text, system prompts, and tool descriptions.</p>
</section>
<section id="pipes">
<h2><span class="num"></span>Pipelines</h2>
<p class="small">A pipeline chains generation, sample checks, and optional repair.</p>
<p class="small">Bars show passes. Labels show price and median time.</p>
<div class="chart floor">{{w_pipes}}</div>
<ul class="tight small">
<li>→H fail: Haiku repairs only failed samples. →H all: Haiku checks every answer.</li>
<li>Sample checks can miss bad answers; they aren't hidden-test guarantees.</li>
<li>⚡ rows reuse cached fast-mode answers. Other pipelines made fresh calls.</li>
<li>The router passed {{router_k}} on held-out repeats.</li>
<li>Its cost was ~{{router_share}} of haiku-high's cost per pass.</li>
</ul>
<details class="small"><summary>Scope</summary>
<ul class="tight small">
<li>{{fast_pipeline_note}}</li>
<li>Router: per main-ladder problem, the cheapest config that passed tries {{router_fit}}. Router evaluation tries: {{router_held}}. The router passed {{router_k}}. That cost ~{{router_share}} of haiku-high's $ per pass.</li>
</ul>
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Fast-mode pipelines matched their builders because every sample check passed without Haiku repairs.</li>
<li>Router choices used early repeats; later repeats independently measured their passes and cost.</li>
</ul>
</details>
</section>
<section id="fair">
<h2><span class="num"></span>Whose bench?</h2>
<p class="small">Does a Codex-built bench favour Codex? {{hb_answer}}</p>
{{chart:harness_bias.svg|{{hb_n_problems}} hard problems, {{hb_repeats}} tries each}}
<ul class="tight small">
<li>The one-shot runner disables tools; vendor agent CLIs allow code runs and retries.</li>
<li>luna-low went {{hb_luna_low_change}}.</li>
<li>haiku-low went {{hb_haiku_low_change}}.</li>
<li>haiku-low led on both benches; routing picks stay unchanged.</li>
<li>The gap moved {{hb_diff_points}} points, below the {{hb_bar_points}}-point bias threshold.</li>
</ul>
<details class="small"><summary>How to read this data</summary>
<h4>The benches</h4>
<ul class="tight small">
<li>{{bench_authorship}}</li>
<li>luna-low ran in Codex CLI, haiku-low in Claude Code: each vendor's cheapest model.</li>
<li>sol61-high was skipped: every try already passed.</li>
</ul>
<h4>What changed</h4>
<ul class="tight small">
<li>Running code cut luna-low's wrong outputs from {{hb_luna_wrong_one}} to {{hb_luna_wrong_agent}}. Crashes fell from {{hb_luna_crash_one}} to {{hb_luna_crash_agent}}.</li>
<li>{{hb_luna_cost}} {{hb_haiku_cost}} Overall, Codex's bench cost {{hb_total_x}} as much per pass.</li>
<li>The gap moved {{hb_diff_points}} points, below our {{hb_bar_points}}-point bias threshold. Confidence level: {{ci_level}}. The range is {{hb_range_points}} points.</li>
<li>Luna-low variants B1 and B2 are listed under Everything we tried. luna-low-noshell-B1 removes shell context and asks for edge cases first. luna-low-noshell-B2 also asks for a detailed reasoning summary. {{noshell_comparison}}</li>
</ul>
<p class="small">Time per pass = summed call seconds divided by passes.</p>
</details>
<details class="small"><summary>How Codex built its bench</summary>
<ul class="tight small">
<li>gpt-6.1-sol high designed and wrote it.</li>
<li>Its dry runs missed two sandbox bugs. A live call found them; Codex fixed both.</li>
<li>A final "plan and reorient" nudge changed no code.</li>
<li>{{hb_subset}}</li>
<li>We lifted its repeat cap, a {{hb_repeat_cap_lines}}-line change, then ran {{hb_full_calls}} calls.</li>
<li>Repeat-cap change source: <code>{{hb_repeat_cap_source}}</code> (bench/codex_harness.py).</li>
<li>It finished with {{hb_errors}} runner errors and no timeouts, in about {{hb_minutes}} minutes.</li>
</ul>
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Codex's bench increased luna-low's cost and time per pass; Haiku's changes were smaller.</li>
<li>Each vendor's cheapest model ran through its own agent CLI.</li>
<li>Edge-case-first prompts helped luna-low; adding detailed reasoning hurt, despite removing shell context in both.</li>
<li>Harness-gap interval: {{hb_range_points}} points; movement remained below the bias threshold.</li>
<li>Time per pass divides summed call seconds by passing attempts.</li>
<li>With code execution, luna-low produced fewer wrong answers and crashes.</li>
<li>sol61-high was excluded from the harness comparison because it already passed every attempt.</li>
</ul>
</details>
</section>
<section class="verdict conclusion" id="conclusion">
<h2 class="eyebrow"><span class="num"></span>CONCLUSION</h2>
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
<h2><span class="num"></span>Limitations</h2>
<ul class="tight small">
<li>A small, self-written set gives routing clues, not a general ranking.</li>
<li>LeetCode analogues and public problem sources create contamination risks.</li>
<li>Config additions after seeing results are exploratory, including our picks.</li>
<li>Partial runs aren't directly comparable; inspect coverage before comparing rates.</li>
<li>L7 perfect score: {{l7_bound}}. Its lower confidence bound is only {{l7_lo}}.</li>
<li>Repo tasks require task completion; few tasks cannot establish skill equivalence.</li>
<li>Cache hits can cut estimated Codex cost by {{cache_swing}}.</li>
<li>Times measure CLI wall clock; up to {{lanes}} calls ran concurrently.</li>
<li>Hosted models change. This measures one run in time.</li>
</ul>
<p class="small">Sources: <a href="https://github.com/chimera-defi/dispatchbench">code, problems, raw results, and full report</a>.</p>
<details class="small"><summary>What could mislead</summary>
<ul class="tight">
<li>Most have a LeetCode analogue, and LeetCode code is widely public.</li>
<li>The problems ship with this repo, so later models can read them.</li>
<li>The {{ci_level}} range resamples whole problems, since tries on the same problem are related.</li>
<li>Repo tasks: luna-low: {{ag_mark_luna_iso}} in the clean-home rerun and every other config completes every run. With {{n_tasks}} tasks × {{agent_repeats}} repeats = {{ag_n}} runs per config they cannot rule out skill differences.</li>
<li>Paired gaps of {{nosep_gap}} points or less showed no separation; {{sep_gap}}-point gaps did.</li>
<li><code>PLAN.md</code> was committed before the main run; a same-day pilot came first.</li>
<li>{{n_exploratory}} configs were added after seeing the main-run results (†). These include the haiku-high and sol61-high picks:<ul>{{exploratory_items}}</ul></li>
<li>We ran up to {{lanes}} calls at once on one host.</li>
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
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Code, problems, and raw results are MIT-licensed on GitHub.</li>
<li>Paired gaps through {{nosep_gap}} points showed no separation; {{sep_gap}}-point gaps did.</li>
<li>Published repository problems can enter later models' training data.</li>
<li>The dataset builds report numbers from stored JSONL runs.</li>
</ul>
</details>
</section>
<section class="extras" id="extras">
<h2><span class="num"></span>Other measures</h2>
<p class="small">Repo tasks: task complete counts visible and hidden tests together.</p>
<p class="small">luna-low completed {{ag_hidden_luna_iso_k}} on hidden tests alone.
</p><p class="small">Its task-complete headline also requires visible tests: {{ag_tc_luna_iso_k}}.</p>
<p class="small">All other configs completed every run.</p>
<p class="small">luna-low failed tests it added itself. Failure classification remains under audit.</p>
<p class="small">A stricter discount test caught boolean input acceptance. Earlier hidden tests missed that bug.</p>
{{chart:agentic.svg|Repo tasks: filled markers count task completion; rings count hidden tests only}}
<details open><summary>Explore tokens, reasoning, and latency</summary>
{{w_any_pair}}
</details>
<details class="small"><summary>Repo-task findings</summary>
<p class="small">{{rung_breaks}}. luna-low-bare breaks at {{bare_rung_break}}; see the grid.</p>
<p class="small">Repo tasks, task complete (hidden in brackets): luna-low {{ag_mark_luna_iso}} in the clean-home rerun ({{ag_mark_luna_orig}} in the original run); every other config completed every run. Every task prompt told agents to add tests and that all tests must pass. {{ag_why_red}} Costs ranged from {{ag_luna_low_usd}} to {{ag_astra_medium_usd}} per run; per complete task luna-low costs {{ag_luna_low_upp}} against haiku-low's {{ag_haiku_low_upp}}.</p>
<p class="small">{{t1v2_line}}</p>
{{table:t1_regrade}}
<p class="small"><b>Correction, 2026-10-28.</b> A reader pointed out that "passed every hidden test" hid luna-low's visible-test misses. The headline is now task complete, with the hidden-suite count beside it.</p>
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Stricter discount regrading reduced only luna-low's hidden passes; headline counts retain their original suite.</li>
<li>{{rung_breaks}}; luna-low-bare breaks at {{bare_rung_break}}.</li>
</ul>
</details>
</section>
<section class="notes" id="notes">
<h2><span class="num"></span>Code quality and evidence</h2>
<details><summary>Code quality</summary>
{{table:quality}}
<p class="small">Complexity counts branches; lint counts style warnings; time and memory compare reference solutions.</p>
<p class="small">The blind review used one reviewer and one solution per cell.</p>
{{table:blind}}
</details>
{{w_everything}}
<p class="small">Sonnet's code read worst in a blind review.</p>
<details class="small"><summary>Codex fast mode and xhigh</summary>
<p class="small">On the {{set_label}}, fast mode kept every pass and was {{fm_faster}} faster. Median times: {{fm_fast_s}} s vs {{fm_ctrl_s}} s. Price: {{fm_mult}} list, not a measured bill. xhigh effort (above high): same passes, {{fm_x_cost}} the cost, slower, no better code.</p>
<p class="small">The blind read covered {{bl_n}} solutions. A code-only reviewer would refuse to merge {{bl_blocks}}, all sonnet-medium. It scored {{bl_sonnet_score}}. Other configs scored {{bl_other_scores}} with none blocked. One reviewer and one solution per cell: a sign of bad code, not a ranking.</p>
<p class="small">{{blind_caption}}</p>
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
<details id="appendix"><summary>Appendix</summary>
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
<li>Since then, terra61-low ⚡ (main ladder and L7) also gives low-effort fast-mode data; see Terra61 at priority tier.</li>
</ul></li>
<li><b>Original repair run: we lost its prompt but reran committed code.</b><ul>
<li>The original luna-low → Haiku-fixes-all run passed {{r_luna_low_haiku_low_repair_k}}.</li>
<li>The rerun from committed code passed {{r_luna_low_haiku_review_all_k}}.</li>
<li>Both use the {{set_label}}, with {{rescue_n}} attempts per row.</li>
</ul></li>
</ul>
</details>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>All {{n_solutions}} solutions are available in results/solutions.</li>
<li>Blind review blocked only sonnet-medium solutions, scoring them below every other config.</li>
<li>Blind review shuffled passing solutions anonymously and scored readability and maintainability.</li>
<li>Codex's main CLI ignored personal settings and disabled tools.</li>
<li>Escalation retested taller_within, best_average, and sheet.</li>
<li>Fast mode accelerates unchanged passes; xhigh costs more, runs slower, and improves no code.</li>
<li>Fast-mode control used a separate {{fm_n}}-attempt default-tier run, distinct from the Results row.</li>
<li>Haiku planning costs more than checking answers afterward.</li>
<li>Haiku plans improved luna-low's passes but left luna-high-bare unchanged.</li>
<li>Harder-set passes: haiku-low {{l7_hl_k}}; sonnet-medium passed all, at higher cost per pass.</li>
<li>Matched pass rates cost {{r_luna_high_bare_haiku_on_fail_upp}} with conditional Haiku repair versus {{r_luna_high_bare_retry_on_fail_upp}} with same-model retries.</li>
<li>On {{q_worst_problem}}, {{q_slow_cfgs}} configs exceed reference runtime, reaching {{q_worst_x}}.</li>
<li>Quality scoring covers {{q_rows}} passing main-ladder solutions.</li>
<li>Radon measures complexity, ruff measures lint; reference ratios below {{ref_unit}} improve; growth-exponent tolerance: {{growth_margin}}.</li>
<li>Repo tasks used a clean Codex home.</li>
<li>Sample checks caught {{g_hi_fixed}} bad answers, all repaired by Haiku, but missed {{g_hi_missed}}.</li>
<li>The harder set contains xor_ring, bounce_board, and paint_erase.</li>
<li>The unchecked luna-high-bare run produced {{r_luna_high_bare_miss}} bad answers.</li>
<li>Too slow means exceeding the grader's per-case time limit.</li>
<li>luna-high passed {{esc_k}} on escalation problems, improving substantially over luna-medium.</li>
</ul>
</details>
</section>
<section id="interesting">
<h2><span class="num"></span>Interesting findings</h2>
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
<h2><span class="num"></span>Codex vs Claude</h2>
<h3>Terra61 at priority tier (exploratory)</h3>
<ul class="tight small">
<li>{{terra_priority_noise}}</li>
<li>{{terra_priority_speed}}</li>
<li>{{terra_priority_l7}}</li>
<li>{{terra_priority_repo}}</li>
<li>{{terra_priority_p04}}</li>
<li>{{terra_priority_cost}}</li>
</ul>
<p class="small">Matches use the cheapest other-vendor config passing at least as often.</p>
<p><b>{{equiv_takeaway}}</b></p>
{{table:equiv_all}}
<p class="small">All rows use the main ladder. Passing equally often doesn't establish equal skill.</p>
<details class="small"><summary>Earlier concise findings</summary>
<ul class="tight small">
<li>Claude usually offers cheaper pass-rate matches; only luna undercuts its match, with more misses.</li>
</ul>
</details>
</section>
