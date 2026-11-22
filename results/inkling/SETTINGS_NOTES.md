# Inkling 2 Mini settings: sources (checked 2026-11-22)
No Mini-specific model card was found (searches surface Inkling 2 Small only; "tbmod/Inkling-mini" is a test fixture). Small guide values are carry-over, unverified for Mini.
| setting | ChatGPT/approved | docs / GGUF | used | source |
|---|---|---|---|---|
| temperature | 1.0 | 1.0 | 1.0 | https://unsloth.ai/docs/models/inkling-2 ; GGUF embedded |
| top_p | 1.0 | 1.0 | 1.0 | same |
| min_p | 0 | 0.0 | 0 | same |
| top_k | 50 | Small guide 0; Mini GGUF embedded 50 | 50 (Mini's own embedded default) | guide above; llama-server /props |
| context | 16384 | "start with 32,768" | 32768 (docs larger, so docs win) | https://unsloth.ai/docs/models/inkling-2 |
| template | --jinja | "use the embedded chat template ... --jinja" | --jinja | same |
| thinking effort | default | GGUF template default high (0.9); TML evaluates Small at xhigh | default (0.9, high); xhigh not used (CPU time) | same; template via /props |
| threads | 6 | no doc guidance | -t 6 -tb 6 (6 physical cores) | operator-approved |
Reasoning budget: docs give no n_predict; operator floor 8192.
