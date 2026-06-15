# RESULTS — Claim-by-claim, with artifact links

This document collates every result claim made by this repository, in the
metric language of §4 of the simulation spec (`02 simspec kether nishida.md`).
Every claim is backed by a machine-checked artifact whose path is given
under each entry. The values shown are taken from
`experiments/wp5/artifacts/claims.json`, which `experiments/wp5/build_claims.py`
re-validates against the source artifacts on every run.

**Epistemic status.** This repository is an *illustration, not proof, of the
philosophical thesis.* The underlying mathematics is known
(Solovay 1976; de Jongh–Sambin; Boolos 1993; Priest 1979); the contribution
is demonstration, verification, and artifacts.

**Headline.** *The same diagonal seed launches a strict unbounded hierarchy
in one environment and provably nothing in the others.*

The cross-environment comparison is **structural, not numeric**. Growth
claims for GL are confined to the **letterless fragment**, in which the
relevant set of theorems is completely classified — there is no sampling
bias because there is no sample.

---

## Claim manifest

The shape used here matches §6 of the spec: each entry is essentially
`{claim, status: proved | refuted, certificate_or_countermodel: path, experiment: id}`.
The `experiments/wp5/artifacts/claims.json` file holds the same data in JSON
and is the single source of truth for both the table at
`experiments/wp5/artifacts/headline_table.md` and the SVG figure at
`experiments/wp5/artifacts/headline_figure.svg`.

### Claim 1 — Classical: liar is unsatisfiable and explodes vacuously (E-B1)

- **Environment.** Classical propositional logic.
- **Seed.** The liar constraint `λ ↔ ¬λ`.
- **Status.**
  - `satisfiable: false` — the seed has no classical model.
  - `vacuous_explosion: true` — because no model satisfies the seed, every
    formula in the language is a (vacuous) consequence by enumeration over
    all `2^n` valuations.
- **Certificate / countermodel.**
  - `experiments/wp4/artifacts/e_b1_classical_explosion.json` —
    `{ satisfiable: false, vacuous_explosion: true, enumeration_size: 2 }`.
  - `experiments/wp4/artifacts/e_b1_classical_explosion_details.json` —
    `sample_vacuity_checks: [true, true, true, true, true]` (five
    independent sample formulas, each confirmed to follow vacuously).
- **§4 metric framing.** Classical handling of the seed = **destroyed**:
  everything follows, so nothing in the language is distinguishable from
  anything else.
- **What is *not* claimed.** This is not a "proof of the philosophical
  thesis"; it is the classical baseline against which the LP and GL rows
  are contrasted.

### Claim 2 — LP: liar is satisfiable, quarantined, and inert (E-B2)

- **Environment.** Priest's Logic of Paradox (LP); designated values `{t, b}`.
- **Seed.** The same liar constraint `λ ↔ ¬λ`.
- **Status.**
  - `satisfiable: true` — the liar has an LP model where `v(λ) = b`.
  - `inert: true` — exhaustive comparison over the λ-free language with
    base atoms `{p, q, r, s}` shows no new λ-free consequences are added by
    the seed (110 formulas considered, 6,106 premise sets, 671,660
    comparisons, 0 violations).
  - `mp_failure = {A: b, B: f}`, `ds_failure = {A: b, B: f}` — concrete
    LP witnesses to the failures of Modus Ponens and Disjunctive Syllogism
    (each requires a value combination involving `b`).
- **Certificate / countermodel.**
  - `experiments/wp4/artifacts/e_b2_lp_quarantine.json` —
    `{ satisfiable: true, inert: true, mp_failure: {A:b, B:f}, ds_failure: {A:b, B:f} }`.
  - `experiments/wp4/artifacts/e_b2_lp_quarantine_details.json` —
    liar witness `v(λ) = b`, `liar_value_at_witness: "b"`, inertness scope
    with `violations: []`.
- **§4 metric framing.** LP handling of the seed = **zero**: the
  contradiction is quarantined at `b`, but the λ-free fragment receives
  *no* new consequences. Generativity, measured as new λ-free
  consequences, is zero.

### Claim 3 — GL: each Con_n is provably distinct from Con_{n+1} (E-A2)

- **Environment.** Gödel–Löb provability logic (GL). The relevant fragment
  is the **letterless fragment**, which is completely classified.
- **Seed.** The Gödelian fixed point `H ↔ ¬□H` and the consistency hierarchy
  `Con_n ≡ ¬□^{n+1} ⊥`.
- **Status.** For every `n ∈ {0, 1, …, 8}`:
  - **Monotone direction `Con_{n+1} → Con_n` is *proved*** by the GL prover
    (signed labelled tableau).
  - **Strict direction `Con_n → Con_{n+1}` is *refuted***: an explicit
    finite Kripke countermodel is exhibited and independently verified by
    the countermodel verifier (`src/gl/countermodel_verifier.py`, distinct
    from the prover).
  - The witnessing model is an `(n+2)`-chain (linear, transitive,
    irreflexive). Witness world counts: `[2, 3, 4, 5, 6, 7, 8, 9, 10]`.
  - **Minimality** of the `(n+2)`-chain is *exhaustively verified* for
    `n ∈ {0, 1, 2, 3, 4}` by enumeration over all finite GL frames of
    bounded height; for `n ∈ {5, 6, 7, 8}` the same linear witness is
    exhibited but minimality is structural, not exhaustive.
- **Certificate / countermodel.**
  - `experiments/wp3/artifacts/ladder_manifest.json` —
    `max_n: 8`, `exhaustive_max: 4`, 9 stages, each with
    `monotone_status: "proved"`, `strict_status: "refuted"`,
    `countermodel_verified: true`.
  - Individual countermodel JSONs:
    `experiments/wp3/countermodels/strict_n0.json` …
    `experiments/wp3/countermodels/strict_n8.json`.
- **§4 metric framing.** GL handling of the seed = **unbounded** (linear
  `n + 2`): each stage requires a strictly deeper Kripke frame than the
  previous one. The comparison with classical/LP is **structural** —
  classical says "everything" (destroyed), LP says "nothing new in the
  λ-free language" (zero), GL says "a strictly higher consistency level".
  The exactness of the growth measurement is preserved because the growth
  lives in the letterless fragment.
- **Triviality objection (§4-1).** `Con_n` is *not* an imported axiom; the
  diagonal engine computes it from the system's own provability structure
  (`src/gl/formula.py:con`, `src/gl/box_power`). The Henkin contrast
  experiment (E-A3) that strengthens this answer further by showing the
  same engine generates nothing from a Henkin seed is **not** implemented
  in this repository; that contrast is referenced from the literature
  (Boolos 1993) and is listed as out of scope here.

### Claim 4 — LP/SK transparent truth predicate: liar quarantined at fixed point (E-C1, optional)

- **Status.** *Optional WP6 deliverable*; first-order upgrade of Claim 2
  (E-B2). Not part of the headline; supplied as a control artifact.
- **Environment.** A finite fragment of a first-order language with a
  transparent truth predicate `T(⌜·⌝)`, evaluated in two schemes:
  Priest's LP (designated values `{t, b}`, complete extension/anti-extension
  pairs, b is bottom in the precision order) and strong-Kleene (designated
  `{t}`, consistent pairs, n is bottom in the knowledge order). The fragment
  contains 9 explicitly coded sentences including the liar `ℓ = ¬T(⌜ℓ⌝)` and
  the truth-teller `τ = T(⌜τ⌝)`. No Gödel numbering is used; codes are
  finite table keys.
- **Seed.** The transparent-truth diagonal `ℓ ↔ ¬T(⌜ℓ⌝)` lifted into the
  truth-predicate language.
- **Status.**
  - `lp_liar_value: "b"` and `sk_liar_value: "n"` at the least fixed point
    of the monotone Kripke-style operator (Kleene iteration from the
    scheme-specific bottom).
  - `least_fixed_point_minimal: true` in both schemes — confirmed by full
    enumeration of the `3⁹ = 19,683` admissible states; the iterated
    least fixed point is `≤` every fixed point in the scheme order.
  - `monotone_operator: true` in both schemes — confirmed by exhaustive
    check of all `118,098` cover edges over the 9-code state space.
  - `inert_first_order: true` in both schemes — over `7,265`
    liar-free formulas generated up to depth 2 from
    `{p, q, T(p), T(q), T(τ)}`, every formula receives the same value
    in the base (liar-free) fragment's least fixed point and the full
    fragment's least fixed point.
  - **Classical contrast.** Under bivalent evaluation the same code table
    has `fixed_point_count: 0` and the iteration trace from the empty
    extension oscillates `[F, T, F, T, F, T, F]` — the liar has no
    classical fixed point on this code table.
- **Certificate.**
  - `experiments/wp6/artifacts/e_c1_fixed_points.json` — LP/SK least fixed
    points, value tables, iteration traces, inertness summary, classical
    contrast.
  - `experiments/wp6/artifacts/e_c1_kat_results.json` — 10 known-answer
    tests (per-scheme liar/truth-teller, no-explosion witness, inertness,
    classical no-fixed-point, full-enumeration minimality).
  - `experiments/wp6/artifacts/e_c1_enumeration_certificates.json` — the
    19,683 / 118,098 / fixed-point-count certificates per scheme.
- **§4 metric framing.** First-order LP/SK handling of the transparent-truth
  diagonal = **zero**: the truth-predicate liar is isolated at `b` (LP)
  or `n` (SK) and the liar-free sublanguage receives no new truth values.
  This is the first-order analogue of Claim 2's quarantine — a
  control artifact contrasted with Claim 3's generative hierarchy, *not*
  an additional row in the headline.
- **What is *not* claimed.** This is an instance of known fixed-point
  constructions (Kripke 1975 and the paraconsistent variants discussed in
  the literature on transparent truth over LP) restricted to a finite
  fragment. It is provided as a machine-checked illustration. It is not a
  novel mathematical result, does not prove the philosophical thesis, and
  does not enlarge the headline claim (which is the GL hierarchy of
  Claim 3).
- **Scope limit.** Inertness is verified over a finite generated
  liar-free fragment (depth 2, 7,265 formulas), not over the whole
  first-order language. Minimality is the least fixed point in the
  precision/knowledge order specific to each scheme (LP precision order
  with `b` as bottom; SK knowledge order with `n` as bottom).

### Claim 5 — Arithmetic: `𝗜𝚺₁ ⪱ 𝗜𝚺₁ + Con(𝗜𝚺₁)` typechecks in Lean 4 (E-C2, optional)

- **Status.** *Optional WP6 deliverable*; arithmetic-side shadow of
  Claim 3 (GL `Con_n` hierarchy) at stage 1. Not part of the headline.
- **Environment.** Lean 4 (`leanprover/lean4:v4.29.0`) with
  [`FormalizedFormalLogic/Foundation`](https://github.com/FormalizedFormalLogic/Foundation)
  pinned at commit `c28942b7d9d0df41ee5b736602c3f27b8643532c`, which in
  turn pins Mathlib at rev `1a37cd3c8e618022c5e78dee604c75c3c946a681`.
  Pins are recorded in
  [`experiments/wp6/lean/lakefile.toml`](experiments/wp6/lean/lakefile.toml)
  and the committed
  [`experiments/wp6/lean/lake-manifest.json`](experiments/wp6/lean/lake-manifest.json).
- **Seed.** The second-incompleteness statement
  `T ⊬ ↑T.consistent` (Foundation,
  `FirstOrder/Incompleteness/Second.lean`), used in its abstract
  provability form. The general instance
  `instance [Consistent T] : T ⪱ T + T.Con` is given by Foundation for
  any `T` with `[T.Δ₁]`, `[𝗜𝚺₁ ⪯ T]`, `[Consistent T]`.
- **Status.**
  - `lake build` exit code 0 — the deliverable file
    [`experiments/wp6/lean/S7Wp6LeanInstantiation.lean`](experiments/wp6/lean/S7Wp6LeanInstantiation.lean)
    typechecks against the pinned Foundation, including its 1,200+
    transitive Mathlib dependencies.
  - The deliverable term:
    ```lean
    theorem wp6_ec2_stage1_ISigma1 : 𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con :=
      inferInstance
    ```
  - Axiom dependency (verified by `#print axioms` at every build):
    `[propext, Classical.choice, Quot.sound, ISigma1_delta1Definable]`.
    The first three are Lean / Mathlib standard axioms; the last is
    Foundation's registered axiom for `𝗜𝚺₁.Δ₁` (Δ₁-definability of
    `𝗜𝚺₁`), which Foundation has not yet derived from its other axioms
    at this commit.
- **Certificate.**
  - [`experiments/wp6/lean/S7Wp6LeanInstantiation.lean`](experiments/wp6/lean/S7Wp6LeanInstantiation.lean) —
    the deliverable theorem and its sibling `#print axioms` directive.
  - [`experiments/wp6/lean/lakefile.toml`](experiments/wp6/lean/lakefile.toml)
    and [`experiments/wp6/lean/lake-manifest.json`](experiments/wp6/lean/lake-manifest.json) —
    full pinned dependency graph.
- **§4 metric framing.** Arithmetic-side handling of the diagonal seed
  at stage 1 = **strictly greater consistency strength**: `Con(𝗜𝚺₁)`
  is unprovable in `𝗜𝚺₁` but trivially provable in `𝗜𝚺₁ + Con(𝗜𝚺₁)`.
  This is the arithmetic shadow of Claim 3's GL `Con_n` hierarchy at
  one stage; the comparison is structural.
- **What is *not* claimed.** This is an instantiation of a known result
  (the Saito–Noguchi formalisation in `FormalizedFormalLogic/Foundation`)
  on a concrete base theory; it is not a novel mathematical contribution.
  The proof's correctness is relative to the consistency of Lean 4's
  type theory and Mathlib's foundational axioms (including
  `Classical.choice`), and additionally to Foundation's
  `ISigma1_delta1Definable` axiom; it is therefore *not* an absolute
  consistency claim for arithmetic. This deliverable does not prove the
  philosophical thesis.
- **Reproduction.** Not included in `make all` (Lean toolchain and
  Mathlib cache are heavy). Reproduce with `make wp6-lean` after
  installing elan; see
  [`experiments/wp6/lean/README.md`](experiments/wp6/lean/README.md)
  for details.

---

## Cross-environment summary

| Environment | Status | Generativity | Witness artifact |
|---|---|---|---|
| Classical | seed unsatisfiable; vacuous explosion | destroyed | `experiments/wp4/artifacts/e_b1_classical_explosion.json` |
| LP | seed satisfiable at `v(λ)=b`; λ-free fragment unchanged | zero | `experiments/wp4/artifacts/e_b2_lp_quarantine.json` |
| GL | each `Con_{n+1} → Con_n` proved, each `Con_n → Con_{n+1}` refuted | unbounded (linear `n+2`) | `experiments/wp3/artifacts/ladder_manifest.json` |

The auto-generated headline rendering of the same data is at
`experiments/wp5/artifacts/headline_table.md` and
`experiments/wp5/artifacts/headline_figure.svg`.

## Verification discipline

- **Every theorem claim** above comes with a prover certificate; every
  non-theorem claim comes with an independently validated countermodel.
- **Two methods, cross-checked.** GL provability is decided by a signed
  labelled tableau and, for finite countermodel search, by independent
  Kripke search. Countermodels emitted by either are validated by a
  separate `countermodel_verifier` that does not reuse prover code (an
  AST-level import check in the test suite enforces this separation).
- **No self-reporting.** The CI workflow at `.github/workflows/test.yml`
  runs `uv run pytest -q`, regenerates every experiment artifact, then
  runs `git diff --exit-code`. Any drift between the committed artifacts
  and a fresh build fails the build.
