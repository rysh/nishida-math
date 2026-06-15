# S7 — WP6 E-C2 Lean instantiation, archived dispatch material

This directory archives the LLM dispatch material for task S7 (WP6 E-C2:
arithmetic-level stage-1 instantiation in Lean 4).

## Files

- **`chatgpt.md`** — ChatGPT GPT-5 response to
  `prompts/single/S7_dispatch.md`. Useful for its environment pinning
  research (Foundation commit, Lean toolchain, Mathlib rev) and as a
  reference draft of the `.lean` file. Confidence: Medium; build not
  locally confirmed by ChatGPT.

## Disposition

The final deliverable was written from scratch by Claude Code, not adopted
from the ChatGPT draft. ChatGPT's research on the pinned commit and the
choice of `𝗜𝚺₁` as the concrete base theory was incorporated; the Lean
code itself was re-derived against the live Foundation API
(`Foundation.FirstOrder.Incompleteness.Examples`, which already contains
`instance : 𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con := inferInstance` at the pinned commit),
using Foundation's actual Unicode notation `𝗜𝚺₁` and Lean 4 `inferInstance`
(not ChatGPT's ASCII `ISigma 1` and Lean 3 style `infer_instance`). The
build was confirmed locally — `lake build` succeeds, axioms verified via
`#print axioms`.

Deliverable lives under `experiments/wp6/lean/`. See
[`RESULTS.md`](../../RESULTS.md) Claim 5 and
[`experiments/wp6/lean/README.md`](../../experiments/wp6/lean/README.md).
