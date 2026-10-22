<p class="meta">Run 2026-10-22b · {{claude_usd}} Claude · {{codex_usd}} Codex (proxy) · <code>make audit</code> checked</p>

# Which model should a coding task go to?

<p class="lede">{{n_configs}} configs, {{n_problems}} post-cutoff Python problems, {{n_tasks}} repo tasks.</p>

<nav class="toc"><a href="#pass-rate-vs-cost">Scatter</a><a href="#where-each-model-fails">Failures</a><a href="#results">Results</a><a href="#tokens-per-call">Tokens</a><a href="#cost-vs-latency">Latency</a><a href="#code-quality">Quality</a><a href="#what-to-do">What to do</a><a href="#details">Details</a></nav>

<div class="winner"><span class="eyebrow">🏆 Routing rule</span>
<b>Default to haiku-low. Cheapest near-equal: luna-high, with a Haiku repair pass on hard problems. When a miss is not an option: sonnet-medium.</b>
<ul><li>haiku-low passes {{haiku_low_pass}} at {{haiku_low_upp}} per pass; luna-high {{luna_high_pass}} at {{luna_high_upp}}.</li>
<li>A haiku-low repair pass took luna-low from {{r_e_luna}} to {{r_luna_low_haiku_low_repair_k}} on its hardest problems.</li>
<li>sonnet-medium never failed ({{sm_all}}), at {{sm_vs_hl_x}} haiku-low's price per pass.</li></ul></div>

## 📊 Pass rate vs cost

{{explorer}}

- luna at low and medium effort is cheap but passes only {{luna_low_pass}} and {{luna_medium_pass}}.

## 🟥 Where each model fails

{{chart:heatmap.svg|Passes out of {{repeats}}.}}

{{chart:pass_by_rung.svg|Pass rate by rung.}}

- p12 breaks most configs by crashing: parse errors and recursion limits.
- luna low/medium fail p04 on the statement's own first example.
- haiku-low is never wrong, only slow: {{hl_timeouts}} timeouts.

## 📋 Results

{{table:result}}

- Click a header to sort. Codex $ is a token-price proxy.

## 🧱 Tokens per call

{{chart:token_in.svg|Mean input tokens per call.}}

- Stripping the Codex harness cuts luna's input {{in_cut}}; accuracy moves {{lb_vs_ll}} pts (CI {{lb_vs_ll_ci}}).

## ⏱️ Cost vs latency

{{chart:cost_time.svg|Purple: Pareto frontier.}}

- haiku-low and luna-high share the cheap, fast corner.

## 🧪 Code quality

{{table:quality}}

- All {{n_solutions}} passing solutions are in [results/solutions/](https://github.com/chimera-defi/model-routing-bench/tree/main/results/solutions).

## 🛠️ Repo tasks

{{chart:agentic.svg|Pass rate vs $ per run.}}

- Every config passed every hidden test; cost per run spans {{ag_spread}}.

## 💡 What to do

1. Default: haiku-low with `claude -p --tools ""`.
2. Cheaper: luna at high effort, never low or medium; let Haiku repair hard cases.
3. Must not fail, or L7-hard: sonnet-medium.
4. On Codex, strip the harness first: input drops {{in_cut}}.

## 📎 Details

<details><summary>Findings in full</summary>

{{section:Can luna run on fewer tokens?}}

{{section:What it found}}

</details>

<details><summary>Every failure, by problem</summary>

{{section:Where they fail}}

</details>

<details><summary>Harder rung (L7)</summary>

{{section:Harder rung (L7), added after the main run}}

</details>

<details><summary>Code quality and repo-task notes</summary>

{{section:Code quality}}

</details>

<details><summary>Method</summary>

{{section:Method}}

</details>

<details><summary>Limitations</summary>

{{section:Limitations}}

</details>

<details><summary>Appendix A: can refinements rescue luna-low?</summary>

{{section:Appendix A: can refinements rescue luna-low? (exploratory, post hoc)}}

</details>

<details><summary>Appendix B: the pilot</summary>

{{section:Appendix B: the pilot (superseded)}}

</details>

<details><summary>What we borrowed from other benchmarks</summary>

{{section:What we borrowed from other benchmarks}}

</details>
