import Foundation.FirstOrder.Incompleteness.Examples

/-!
# WP6 E-C2 — stage-1 arithmetic-side instantiation

This file is an **instantiation** of the existing second-incompleteness
formalisation in `FormalizedFormalLogic/Foundation`. No new mathematics is
claimed here.

## What Foundation gives us

`Foundation/FirstOrder/Incompleteness/Second.lean` proves, for every theory
`T : Theory ℒₒᵣ` with `[T.Δ₁]`, `[𝗜𝚺₁ ⪯ T]`, `[Consistent T]`:

```lean
theorem consistent_unprovable [Consistent T] : T ⊬ ↑T.consistent
instance  [Consistent T] : T ⪱ T + T.Con
```

`Foundation/FirstOrder/Incompleteness/Examples.lean` then exhibits the
concrete instances for `𝗜𝚺₁` and `𝗣𝗔`:

```lean
instance : 𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con := inferInstance
instance : 𝗣𝗔 ⪱ 𝗣𝗔 + 𝗣𝗔.Con   := inferInstance
```

## What this file adds

A single named theorem that selects `𝗜𝚺₁` as the concrete base theory and
restates the strict-strengthening instance under a name we can cite from the
project's RESULTS manifest. Importing `Examples` is sufficient because the
`Δ₁`-definability axiom for `𝗜𝚺₁` is registered there as an instance.

The meaning of the resulting term: `Con(𝗜𝚺₁)` is *not* provable in `𝗜𝚺₁`
(Gödel's second incompleteness theorem in the abstract provability form
recorded by Foundation), but is provable in `𝗜𝚺₁ + 𝗜𝚺₁.Con` simply because
that theory adjoins the consistency statement as an axiom. Hence the
extension is a *genuine* strengthening at stage 1 — the arithmetic-side
shadow of the GL-side `Con_n` hierarchy used in this repository's E-A2.

## Caveats

* **Axiom dependency.** Foundation at the pinned commit registers
  `ISigma1_delta1Definable : 𝗜𝚺₁.Δ₁` as an `axiom`, not as a derived
  theorem. The compiled term below therefore depends on this axiom in
  addition to Lean / Mathlib's standard trusted base. Run
  `#print axioms wp6_ec2_stage1_ISigma1` to see the full axiom list.

* **Relative consistency.** This is a Lean 4 typechecking artifact: the
  meaningfulness of the result is relative to the consistency of Lean's
  type theory together with Mathlib's foundational axioms (which include
  classical logic, choice, propext, etc.). This file does *not* establish
  absolute consistency of arithmetic and does *not* prove any philosophical
  thesis.
-/

namespace LO.FirstOrder.Arithmetic

/--
WP6 E-C2 deliverable: the concrete stage-1 strict strengthening
`𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con`, obtained by instance synthesis from Foundation's
second-incompleteness development. This is an *instantiation* of a known
result (Saito, Noguchi et al., `FormalizedFormalLogic/Foundation`).
-/
theorem wp6_ec2_stage1_ISigma1 : 𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con :=
  inferInstance

-- Make the underlying axiom dependency visible at every build.
-- Expected: ISigma1_delta1Definable, propext, Classical.choice, Quot.sound.
#print axioms wp6_ec2_stage1_ISigma1

end LO.FirstOrder.Arithmetic
