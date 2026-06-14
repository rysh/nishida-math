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
