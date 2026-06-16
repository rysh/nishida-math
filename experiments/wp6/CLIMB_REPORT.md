# Climbing report — how far the ladder goes and why it stops

Two qualitatively different walls bound the two ladders in this project.
This report records, with build and enumeration evidence, where each one
sits and why.

## A. Arithmetic-side Lean (Foundation `c28942b...`)

### Result

Stages 1 through 10 of the iterated-consistency ladder all typecheck for
the concrete base theory `𝗜𝚺₁`, with no new axioms beyond what stage 1
already required.

| Stage | Theorem | `lake build` exit | New axioms vs stage 1 |
|---|---|---|---|
| 1 | `𝗜𝚺₁ ⪱ 𝗜𝚺₁ + 𝗜𝚺₁.Con`         | 0 | — (base set: `{propext, Classical.choice, Quot.sound, ISigma1_delta1Definable}`) |
| 2 | `T₁ ⪱ T₁ + T₁.Con` where `T₁ := 𝗜𝚺₁ + 𝗜𝚺₁.Con` | 0 | none |
| 3 | `T₂ ⪱ T₂ + T₂.Con` where `T₂ := T₁ + T₁.Con`     | 0 | none |
| 4 | `T₃ ⪱ T₃ + T₃.Con` | 0 | none |
| 5 | `T₄ ⪱ T₄ + T₄.Con` | 0 | none |
| 6 | `T₅ ⪱ T₅ + T₅.Con` | 0 | none |
| 7 | `T₆ ⪱ T₆ + T₆.Con` | 0 | none |
| 8 | `T₇ ⪱ T₇ + T₇.Con` | 0 | none |
| 9 | `T₈ ⪱ T₈ + T₈.Con` | 0 | none |
| 10 | `T₉ ⪱ T₉ + T₉.Con` | 0 | none |

Reproduce with `make wp6-lean`. `#print axioms` is emitted at every build
for each of the ten theorems; the output is the same four axioms
throughout.

Stage 10 is the **hard cap** chosen by the report writer, not a wall.
The instance graph at stage 10 still resolves cleanly; the cap exists
only to keep the artifact small and the build time bounded. There is no
in-Foundation obstruction to going higher in the same shape.

### The bridge — what Foundation does *not* supply automatically

The generic instance proved in `Foundation/FirstOrder/Incompleteness/Second.lean`
is:

```lean
instance [Consistent T] [T.Δ₁] [𝗜𝚺₁ ⪯ T] : T ⪱ T + T.Con
```

For `T := 𝗜𝚺₁` (stage 1) all three prerequisites are registered as
instances in `Examples.lean` and Foundation's instance graph.

For `T := 𝗜𝚺₁ + 𝗜𝚺₁.Con` (stage 2) the prerequisites are still
auto-derivable: `Consistent` follows by the TA-soundness chain
`[ℕ ⊧ₘ* T] → Consistent T` (the instance in `Consistency.lean:88`); `Δ₁`
follows from the singleton instance on `T.Con` combined with `𝗜𝚺₁.Δ₁`;
`𝗜𝚺₁ ⪯ T` follows from reflexivity-plus-extension.

For `T := T_{k+1}` with `k ≥ 1` (i.e. stage 3 and up), `Consistent` and
`Δ₁` are still automatic, but `𝗜𝚺₁ ⪯ T` is **not** found by
`inferInstance`. The lemma required for the trans-closure
(`Entailment.WeakerThan.trans`) is present and applies cleanly, but it is
not a registered `instance`, so the synthesis algorithm cannot use it.

The diagnostic probes in `experiments/wp6/lean/S7Wp6LeanInstantiation.lean`
record this: `_probe_a, _probe_b, _probe_c, _probe_d` resolve by
`inferInstance`; `_probe_e` does not. The fix is a one-line bridge
proved by hand:

```lean
theorem br_T₃ : 𝗜𝚺₁ ⪯ T₃ :=
  Entailment.WeakerThan.trans (𝓢 := 𝗜𝚺₁) (𝓣 := T₂) (𝓤 := T₃)
    inferInstance inferInstance
attribute [instance] br_T₃
```

and similarly for stages 4 through 10. This is *not new formalization*:
the lemma stitched together (`WeakerThan.trans`) lives in Foundation,
and the bridge just registers, for each concrete `Tₙ`, the trans-closure
instance that the existing automated graph fails to assemble.

### Iterated-Con / Turing–Feferman progressions in Foundation

There is none. Searching the pinned commit's `Foundation/FirstOrder/`
tree for `Turing`, `Feferman`, `progression`, `ordinal-indexed Con`,
`tower`, or any `def Conₙ : ℕ → ArithmeticTheory`-style recursive
extension yields no match. The existing `Iteration.lean` and
`Ordinal.lean` files at this commit live elsewhere (set theory, etc.)
and do not connect to the incompleteness development.

Consequence: the climb above happens stage-by-stage with a hand-written
bridge per stage, not through a general iterated-extension lemma. A
general iterated-extension (`Nat → ArithmeticTheory` plus the
associated instance derivation, including the limit case) would be new
formalization in the Turing–Feferman style; per the explicit guardrail
of the source instruction we did *not* attempt it.

### Ceiling

Stage 10, by report choice. Foundation provides enough to keep going in
exactly the same shape; the practical limit is the size of the
explicitly written `Tₙ` definitions (which double each stage when
unfolded), not anything in the underlying instance graph.

## B. GL-side minimality enumeration

### Result

Minimality of the `(n+2)`-world refuter of `Con_n → Con_{n+1}` is now
exhaustively verified for `n ∈ {0, 1, 2, 3, 4, 5}`. Previous artifact:
`n ≤ 4`. Frame counts examined per stage:

| `n` | frames examined to confirm minimality |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | 4 |
| 3 | 11 |
| 4 | 51 |
| 5 | 408 |

Re-run wall-clock: under one second for the whole ladder (much faster
than the original conservative estimate that recommended stopping at
`n=5`). For `n ∈ {6, 7, 8}` the structural `(n+2)`-chain witness is
still exhibited and verified, but minimality remains structural — not
exhaustive — as before.

### Wall

Frame enumeration. The check at stage `n` enumerates transitive
irreflexive Kripke frames on up to `n+1` worlds, pruning by transitivity
and modal-depth bound. Counts grow ~8× per stage in the observed
range (1 → 2 → 4 → 11 → 51 → 408). Extrapolating, `n=6` would be on
the order of 3,000 frames; `n=7` on the order of 24,000; `n=8` on the
order of 200,000. The actual practical wall sits somewhere in this
range (it has not yet been measured directly because the conservative
`exhaustive_max=5` setting bypasses it).

The cost is dominated by the bitmask-enumerated set of inter-world
edges and the per-frame transitivity check; both scale super-polynomially
in the number of worlds.

## C. Two qualitatively different walls

The contrast itself is part of the deliverable.

- **Arithmetic side (A)**: the limit on automatic climbing is the
  *shape of the library's instance graph*. Foundation supplies enough
  raw mathematical material for stage 2 to be automatic and for any
  later stage to be automatic *given a one-line bridge* that registers
  the trans-closure of `𝗜𝚺₁ ⪯ Tₙ`. The wall is not mathematical; it is
  a structural choice in how Foundation packages its lemmas. A general
  iterated-extension treatment (Turing–Feferman) would change this, but
  it does not exist in Foundation at the pinned commit and is explicitly
  out of scope here.

- **GL side (B)**: the limit on exhaustive minimality verification is
  *raw computational cost*. There is no library-shape question: the
  GL prover and countermodel verifier are complete tools and run
  identically at any `n`. The wall is exponential frame enumeration.
  Past `n ≈ 6` the cost grows fast enough that the structural argument
  becomes the relevant evidence rather than the exhaustive one.

This is the qualitative contrast the report keeps visible: the
arithmetic-side wall is a *library-mathematics* wall, the GL-side wall
is a *computation* wall.

## D. On stage 1 (or any finite stage) being the ceiling

The source instruction (`instructions20260615/I2_how_many_stages.md`)
asked to consider whether stage 1 being the ceiling would constitute a
failure. It does not, and the same applies to any finite stage: the
project's philosophical reading is *possible infinity*, not *completed
infinity*. The roles of the two ladders are complementary, not
redundant:

- The GL-side ladder (Claim 3) carries the "the chain never closes"
  content. Each stage is refuted by a deeper countermodel, and that
  pattern is exhibited structurally to `n=8` (and exhaustively to
  `n=5`).

- The arithmetic-side Lean (Claim 5) carries the "one step is a real
  strengthening in actual arithmetic, not just modal logic" content. A
  single typechecked stage already suffices for that role.

Reaching stage 10 by Foundation is therefore an *unexpected upside*
(more armor than required by the philosophical claim), not a load-bearing
property. The report stops at 10 to keep the artifact compact.

## Reproduction

```bash
# Arithmetic side
make wp6-lean                                  # 11 theorems, ~1–2 min build
# (Lean toolchain pulls Foundation + Mathlib cache on first run.)

# GL side
uv run python experiments/wp3/build_ladder.py  # regenerates ladder_manifest.json
uv run python experiments/wp3/build_figure.py  # regenerates ladder_figure.svg
make verify                                    # determinism check covers both
```

Pinned environment is unchanged from v0.2.0: Lean `v4.29.0`,
Foundation commit `c28942b7d9d0df41ee5b736602c3f27b8643532c`, Mathlib
`1a37cd3c8e618022c5e78dee604c75c3c946a681`.
