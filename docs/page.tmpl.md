<header class="head">
<h1>DispatchBench: which model should a coding task go to?</h1>
<nav class="toc" aria-label="Contents"><a href="#winner">Winner</a><a href="#pareto">Cost vs accuracy</a><a href="#results">Results</a><a href="#problems">Problems</a><a href="#grok">Grok and Devin</a><a href="#method">Method</a><a href="#fail">Failures</a><a href="#tokens">Input tokens</a><a href="#pipes">Pipelines</a><a href="#fair">Whose bench?</a><a href="#limits">Limitations</a><a href="#extras">Other measures</a><a href="#notes">Notes</a><a href="#equiv">Codex vs Claude</a></nav>
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
<h2><span class="num"></span>Cost vs accuracy</h2>
{{w_explorer}}
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
{{w_result_notes}}
</details>
</section>
<section id="problems">
<h2><span class="num"></span>Problems: try them yourself</h2>
<p class="small">Fresh problems, ordered by this bench's difficulty rungs.</p>
<p class="small">LeetCode links show analogues; E/M/H badges show our difficulty guesses.</p>
<ul class="tight small">{{w_problems}}</ul>
</section>
<section id="grok">
<h2 id="grok-and-devin"><span class="num"></span>Grok and Devin</h2>
{{w_grok_summary}}
</section>
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
</section>
<section id="fail">
<h2><span class="num"></span>Where they fail</h2>
<script type="application/json" id="data">__DATA__</script>
<p class="small">{{worst_failure}}.</p>
<p class="small">Cells show passed/attempted; dashes mean untested. Scroll sideways for more configs.</p>
{{w_grid}}
<ul class="tight small">
<li>haiku-low never gave a wrong answer.</li>
<li>Main-ladder misses: {{hl_main_timeouts}} timeouts and {{hl_main_crashes}} crash.</li>
<li>Its {{l7_hl_fail}} L7 misses were timeouts.</li>
</ul>
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
<details><summary>Explore tokens, reasoning, and latency</summary>
{{w_any_pair}}
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
</section>
<section id="equiv">
<h2><span class="num"></span>Codex vs Claude</h2>
<p class="small">Matches use the cheapest other-vendor config passing at least as often.</p>
{{table:equiv_all}}
<p class="small">All rows use the main ladder. Passing equally often doesn't establish equal skill.</p>
</section>
