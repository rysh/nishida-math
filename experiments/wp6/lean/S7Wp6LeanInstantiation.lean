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

/--
WP6 I2 — stage 2 probe.

We attempt the next step
  (𝗜𝚺₁ + 𝗜𝚺₁.Con) ⪱ (𝗜𝚺₁ + 𝗜𝚺₁.Con) + (𝗜𝚺₁ + 𝗜𝚺₁.Con).Con
by reusing the generic second-incompleteness instance with
`T := 𝗜𝚺₁ + 𝗜𝚺₁.Con`. The success or failure of this `inferInstance`
call is itself the deliverable: it tells us whether Foundation
provides, out of the box, the three prerequisites for the extended
theory — `Δ₁`-definability, `𝗜𝚺₁ ⪯ T`, and consistency.
-/
theorem wp6_i2_stage2_ISigma1 :
    (𝗜𝚺₁ + 𝗜𝚺₁.Con) ⪱ (𝗜𝚺₁ + 𝗜𝚺₁.Con) + (𝗜𝚺₁ + 𝗜𝚺₁.Con).Con :=
  inferInstance

#print axioms wp6_i2_stage2_ISigma1

-- WP6 I2 — diagnostic finding for the stage-3 ceiling.
--
-- Of the three prerequisites for `T ⪱ T + T.Con` at `T := stage-N base`
-- for N ≥ 2, two (`Δ₁`-definability and `Consistent`) are auto-derivable by
-- Foundation's existing instance graph. The third, `𝗜𝚺₁ ⪯ T`, is not:
-- Foundation does not propagate `𝗜𝚺₁ ⪯ T` through multiple `+ _.Con` steps
-- via instance synthesis. The lemma needed for the trans-closure
-- (`Entailment.WeakerThan.trans`) is present and applies cleanly, but it is
-- not a registered `instance`, so `inferInstance` does not find it. We
-- therefore add a one-line bridge for each new stage and reuse the original
-- generic `T ⪱ T + T.Con` to close that stage. No new formalisation;
-- existing Foundation lemmas in different namespaces are stitched together.

abbrev T2 : ArithmeticTheory := 𝗜𝚺₁ + 𝗜𝚺₁.Con
abbrev T3 : ArithmeticTheory := T2 + T2.Con
abbrev T4 : ArithmeticTheory := T3 + T3.Con
abbrev T5 : ArithmeticTheory := T4 + T4.Con
abbrev T6 : ArithmeticTheory := T5 + T5.Con
abbrev T7 : ArithmeticTheory := T6 + T6.Con
abbrev T8 : ArithmeticTheory := T7 + T7.Con
abbrev T9 : ArithmeticTheory := T8 + T8.Con
abbrev T10 : ArithmeticTheory := T9 + T9.Con

-- A one-line bridge per stage: 𝗜𝚺₁ ⪯ Tₙ, via `WeakerThan.trans` on the
-- previous bridge and the immediate Tₙ₋₁ ⪯ Tₙ.

theorem br_T3 : 𝗜𝚺₁ ⪯ T3 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T2) (𝓤 := T3)
    inferInstance inferInstance
attribute [instance] br_T3

theorem br_T4 : 𝗜𝚺₁ ⪯ T4 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T3) (𝓤 := T4)
    inferInstance inferInstance
attribute [instance] br_T4

theorem br_T5 : 𝗜𝚺₁ ⪯ T5 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T4) (𝓤 := T5)
    inferInstance inferInstance
attribute [instance] br_T5

theorem br_T6 : 𝗜𝚺₁ ⪯ T6 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T5) (𝓤 := T6)
    inferInstance inferInstance
attribute [instance] br_T6

theorem br_T7 : 𝗜𝚺₁ ⪯ T7 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T6) (𝓤 := T7)
    inferInstance inferInstance
attribute [instance] br_T7

theorem br_T8 : 𝗜𝚺₁ ⪯ T8 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T7) (𝓤 := T8)
    inferInstance inferInstance
attribute [instance] br_T8

theorem br_T9 : 𝗜𝚺₁ ⪯ T9 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T8) (𝓤 := T9)
    inferInstance inferInstance
attribute [instance] br_T9

theorem br_T10 : 𝗜𝚺₁ ⪯ T10 :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T9) (𝓤 := T10)
    inferInstance inferInstance
attribute [instance] br_T10

-- The stage theorems themselves. Each is one `inferInstance` once the
-- corresponding bridge is registered.

/-- WP6 I2 — stage 3 probe. -/
theorem wp6_i2_stage3_ISigma1 : T3 ⪱ T3 + T3.Con := inferInstance
#print axioms wp6_i2_stage3_ISigma1

/-- WP6 I2 — stage 4 probe. -/
theorem wp6_i2_stage4_ISigma1 : T4 ⪱ T4 + T4.Con := inferInstance
#print axioms wp6_i2_stage4_ISigma1

/-- WP6 I2 — stage 5 probe. -/
theorem wp6_i2_stage5_ISigma1 : T5 ⪱ T5 + T5.Con := inferInstance
#print axioms wp6_i2_stage5_ISigma1

/-- WP6 I2 — stage 6 probe. -/
theorem wp6_i2_stage6_ISigma1 : T6 ⪱ T6 + T6.Con := inferInstance
#print axioms wp6_i2_stage6_ISigma1

/-- WP6 I2 — stage 7 probe. -/
theorem wp6_i2_stage7_ISigma1 : T7 ⪱ T7 + T7.Con := inferInstance
#print axioms wp6_i2_stage7_ISigma1

/-- WP6 I2 — stage 8 probe. -/
theorem wp6_i2_stage8_ISigma1 : T8 ⪱ T8 + T8.Con := inferInstance
#print axioms wp6_i2_stage8_ISigma1

/-- WP6 I2 — stage 9 probe. -/
theorem wp6_i2_stage9_ISigma1 : T9 ⪱ T9 + T9.Con := inferInstance
#print axioms wp6_i2_stage9_ISigma1

/-- WP6 I2 — stage 10 probe (hard cap). -/
theorem wp6_i2_stage10_ISigma1 : T10 ⪱ T10 + T10.Con := inferInstance
#print axioms wp6_i2_stage10_ISigma1

end LO.FirstOrder.Arithmetic
