# E-A3 implementation notes

## What was reused

* `gl.fixed_point.fixed_point(A, p)` — the de Jongh / Sambin construction. Both
  seeds go through this single function with no special-casing.
* `gl.tableau.prove_gl` — the GL decision procedure used to classify both
  fixed points (Henkin = theorem, Gödel = non-theorem) and to verify all
  letterless equivalences.
* `gl.formula.con(n)` — the canonical `Con_n` form `¬□^{n+1}⊥` from
  `src/gl/formula.py:149`. This is the same closed-form representation that
  `gl.letterless` uses, which keeps the measure consistent across the two
  sides.
* `gl.letterless.nf_equiv` — letterless GL-equivalence by canonical normal
  form; used to certify that `H_godel` is letterless-equivalent to
  `con(0) = ¬□⊥` and that `H_henkin` is letterless-equivalent to `Not(bot()) = ⊤`.

No new prover, no new fixed-point algorithm, no new normal-form reducer.

## How "same measure" is enforced

The two seeds are compared on the letterless fragment. The metric is GL-provable
consequence at fixed depth: for the Henkin side we check that for every `B` in a
small letterless sample, `GL ⊢ (K → B) ↔ B`; for the Gödel side we check that
the analogous implication `H_godel → Con_{n+1}` is refuted for `n = 0..4`.

Both checks are calls to `prove_gl`. The Henkin side comes out "all unchanged"
(flatline). The Gödel side comes out "all refuted" (the higher rungs are
genuinely new, witnessed by the existing E-A2 strict-`n` countermodels in
`experiments/wp3/countermodels/`).

## Which route was used for "Henkin = ⊤"

The direct route: `prove_gl(Iff(H_henkin, Not(bot()))).status == "proved"`,
where `H_henkin = fixed_point(Box(atom("p")), "p")`. The fixed-point engine's
simplifier already normalises `Box(Not(bot()))` to `Not(bot())`, so the
returned formula is the syntactic top constant; the prover certifies the
biconditional anyway.

We also report `prove_gl(H_henkin).status == "proved"` separately as a
single-formula classification — Henkin's fixed point is a GL theorem in its
own right (by Löb), which is the structural ground for the flatline.

## Stage 0 boundary

`H_godel = Not(Box(bot()))` is syntactically equal to `con(0)`, so the
"reduction to Con_0" check is trivially proved. We still issue the
biconditional `prove_gl(Iff(H_godel, con(0)))` and certify it via the prover,
to keep the asymmetry explicit and reproducible on later refactors where the
simplifier might output a different syntactic form.

## What is *not* claimed

* This is an instantiation of Boolos 1993 (Löb's theorem applied to the
  Henkin fixed point). The mathematics is not new.
* The "active ingredient is negative self-reference, not contradiction" is a
  §4-metric reading of the artifact, not a philosophical proof. The artifact
  classifies two seeds under a shared measure; the philosophical reading is
  reported in `RESULTS.md` per the existing illustration-not-proof discipline.

## Open ends

* The letterless sample in `e_a3_henkin_flatline.json` is small (seven
  formulas including `Con_0, Con_1, Con_2, □^3⊥`). A larger sample is
  unnecessary because the equivalence `(K → B) ↔ B` is provable in GL for
  *every* letterless `B` (since `K ↔ ⊤`); the sample is illustrative
  evidence, not a coverage claim.
* The Gödel chain check stops at `n = 4`. Extending it would just lengthen the
  artifact without telling us anything `experiments/wp3/` does not already
  certify exhaustively for `n ≤ 4` (and structurally for `n ≤ 8`).
