# WP6 E-C2 — Lean 4 stage-1 instantiation

A single machine-checked instance of *"the consistency extension is a
genuine strengthening"* for the concrete arithmetic base theory `𝗜𝚺₁`,
obtained by instantiation from
[`FormalizedFormalLogic/Foundation`](https://github.com/FormalizedFormalLogic/Foundation)'s
existing second-incompleteness development.

This is an **optional WP6 deliverable**. It is not required by the
headline claim of the repository (which is the GL `Con_n` hierarchy of
E-A2). It is provided as the arithmetic-side shadow of that hierarchy at
stage 1.

## Result

```lean
theorem wp6_ec2_stage1_ISigma1 : 𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con :=
  inferInstance
```

(see [`S7Wp6LeanInstantiation.lean`](S7Wp6LeanInstantiation.lean)).

`⪱` is `StrictlyWeakerThan`. The body is a single `inferInstance` call;
all of the mathematical content is in Foundation.

## What's pinned

| Component        | Version                                              |
|------------------|------------------------------------------------------|
| Lean toolchain   | `leanprover/lean4:v4.29.0`                           |
| Foundation       | commit `c28942b7d9d0df41ee5b736602c3f27b8643532c`    |
| Mathlib (via Foundation manifest) | rev `1a37cd3c8e618022c5e78dee604c75c3c946a681` |

The `lake-manifest.json` produced by `lake update` records every
transitive dependency revision and is committed alongside the lakefile so
that any later checkout reproduces the same build.

## Reproduce the build

Requires [elan](https://lean-lang.org/lean4/doc/setup.html). The repo's
`make all` does **not** include this build — Lean is heavyweight and the
deliverable is optional. Run it explicitly:

```bash
# from the repo root
make wp6-lean
# or, equivalently, from this directory:
lake update
lake exe cache get      # download the Mathlib olean cache (several hundred MB)
lake build
```

Expected outcome: `lake build` exits with status 0 and the theorem
`LO.FirstOrder.Arithmetic.wp6_ec2_stage1_ISigma1` typechecks.

To see the underlying axioms the proof depends on, temporarily add the
line

```lean
#print axioms wp6_ec2_stage1_ISigma1
```

at the end of `S7Wp6LeanInstantiation.lean` and rebuild. You should see
`ISigma1_delta1Definable` listed alongside the standard Lean / Mathlib
axioms (`Classical.choice`, `propext`, `Quot.sound`). Foundation at this
commit ships `𝗜𝚺₁.Δ₁` as an axiom rather than a derived theorem; this is
acknowledged in [`docs/wp6_survey.md`](../../../docs/wp6_survey.md).

## What is and is not claimed

* This file produces a machine-checked Lean 4 term for the stage-1 strict
  strengthening at a concrete base theory. It is an *instance* of a known
  result, not new mathematics.

* It is the arithmetic-side counterpart of the GL `Con_n` hierarchy in
  E-A2; the connection is structural, not a derivation of one from the
  other.

* It does **not** establish absolute consistency of arithmetic. Lean's
  own consistency is relative to ZFC plus large-cardinal assumptions; the
  result inherits this relativisation.

* It does **not** prove any philosophical thesis. This repository is an
  illustration, not a proof, of the philosophical thesis.

* Library attribution: Foundation is maintained by
  [Palalansoukî (Shogo Saito)](https://github.com/iehality) and
  [SnO2WMaN (Mashu Noguchi)](https://github.com/SnO2WMaN). License:
  Apache-2.0.

## Troubleshooting

* **`lake: command not found`** — install elan first:
  `curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y`
* **`lake exe cache get` is slow** — Mathlib's olean cache is hundreds of
  megabytes. Allow several minutes on first run.
* **`lake build` rebuilds Mathlib** — usually means the cache step failed
  silently. Re-run `lake exe cache get` before `lake build`; check
  network connectivity.
