# Devin stage log (swe-1-6-slow, free tier)
- Stage 1 (p01-p12 x 1, 2026-10-28): 12 calls, no stop/cap message, 6/12 pass (passed p01, p02, p03, p05, p08, p10; timeouts p04, p11; wrong p06, p07, p09; crash p12). Median wall 10.5 s.
- Stage 2 not run: rule needs >= 9/12 on stage 1.

# swe-2-flash-medium (Free), 2026-11-25, PLAN.md deviation 28
- swe-2-1* and the other SWE-2 models: `Error: Upgrade to Pro to access this model (https://devin.ai/pricing)`; not run.
- Stage 1 (p01-p12 x 1): 11/12, no stop message (failed p08 IndexError on a small case). Stage 2 (repeats 2-5) ran: 60 calls, 48/60, no cap, quota or upgrade message.
