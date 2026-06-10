# Simulation Specification — Generative vs. Inert Contradiction

*(project ケーテル西田 / paper: “Generative Contradiction: Nishida Kitarō and Gödel’s Incompleteness” — companion computational study. Spec v1, 2026-06-10. For coding agents; self-contained.)*

-----

## 0. Background for agents (read this even with zero project context)

The paper argues that Nishida Kitarō’s 絶対矛盾的自己同一 (absolute contradictory self-identity) and Gödel’s incompleteness theorem describe the same structure — **productive self-reference**: a self-referential gap that perpetually generates new truth. The paper distinguishes three logical environments for “contradiction”:

1. **Classical** — contradiction = explosion (system death).
1. **Paraconsistent (LP)** — contradiction = tolerated but **inert** (quarantined; generates nothing; costs inferential power).
1. **Generative (Gödel/provability)** — the self-referential gap launches a **strictly increasing, never-collapsing hierarchy** of new truths.

Your job: build a small, fully verified computational exhibit of this three-way contrast. All underlying mathematics is **known** (Solovay 1976; de Jongh–Sambin; Boolos 1993; Priest 1979). The contribution is **demonstration, verification, and artifacts** (machine-checked proofs, explicit countermodels, figures) — not new theorems. Do not claim novelty for the math; do not claim the simulations prove the philosophical thesis. They **illustrate** it.

Full project context (optional reading): `00_ideas_ケーテル西田_v2.md`.

-----

## 1. Headline experiment: ONE SEED, THREE ENVIRONMENTS

The same diagonal (self-referential) seed is planted in three logical environments. Predicted outcomes:

|Environment                   |Seed                        |Outcome                                                                                                                                                                        |
|------------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Classical propositional logic |liar constraint λ ↔ ¬λ      |**Explosion** — unsatisfiable; everything follows; system dies                                                                                                                 |
|LP (Priest’s Logic of Paradox)|same liar constraint λ ↔ ¬λ |**Quarantine** — satisfiable (v(λ)=b); nothing new follows in the λ-free language; modus ponens & disjunctive syllogism lost                                                   |
|GL (provability logic)        |Gödelian fixed point H ↔ ¬□H|**Generation** — resolves to H ≡ ¬□⊥ (= Con); adding it launches the strict hierarchy Con₀ ⊊ Con₁ ⊊ Con₂ ⊊ … with explicit countermodels witnessing non-collapse at every stage|

This table, computed and verified, is the headline figure of the companion. Every cell must be backed by a machine-checked artifact.

-----

## 2. Formal background and known results (do not re-derive incorrectly; unit-test against this section)

### 2.1 GL (Gödel–Löb provability logic)

- **Language:** propositional + unary □. ◇A := ¬□¬A. ⊥ primitive.
- **Axioms:** classical tautologies; K: □(A→B)→(□A→□B); **Löb:** □(□A→A)→□A. Rules: modus ponens, necessitation. (The 4-axiom □A→□□A is derivable in GL.)
- **Semantics:** finite, transitive, **irreflexive** (conversely well-founded) Kripke frames. GL is sound and complete for these; **finite model property ⇒ decidable** (Segerberg 1971).
- **Arithmetical meaning (Solovay 1976):** GL is exactly the logic of the formal provability predicate of PA. □ = “provable in the base system F.” So GL-level results are results about the *structure of provability* — this is why the GL level suffices for the paper.

### 2.2 Fixed-point theorem (the diagonal lemma, modally)

For any formula A(p) in which **p occurs only under □** (“p modalized in A”), there exists H (in the other variables of A) with:

GL ⊢ H ↔ A(H)

- **Existence:** de Jongh; Sambin (independently, mid-1970s). **Uniqueness** up to GL-provable equivalence: Bernardi; de Jongh. The construction is **effective** — there is an algorithm. Implementation references: **Boolos, *The Logic of Provability* (1993)** (primary); Smoryński, *Self-Reference and Modal Logic* (1985) (alternative).
- This is the formal counterpart of “specifying an object by the constraint it places on itself.”

**Known-answer tests (KATs) — your fixed-point engine MUST reproduce these, verified by your own GL prover:**

|A(p)  |Fixed point H|Reading                                                                         |
|------|-------------|--------------------------------------------------------------------------------|
|¬□p   |¬□⊥          |Gödel sentence (“I am unprovable”) ≡ consistency                                |
|□p    |⊤            |Henkin sentence (“I am provable”) — **inert** (Löb’s theorem)                   |
|□p → q|□q → q       |Löb sentence                                                                    |
|□¬p   |□⊥           |“I prove my own negation(’s provability)” — verified via Löb instance □(□⊥→⊥)→□⊥|

(KAT verification of row 1, for your unit tests: H ↔ ¬□H reduces to □⊥ ↔ □¬□⊥. →: from □⊥, □-monotonicity. ←: ¬□⊥ ≡ (□⊥→⊥), so □¬□⊥ ≡ □(□⊥→⊥), and Löb with A:=⊥ gives □(□⊥→⊥)→□⊥. ∎)

For all other inputs the engine computes H and the prover **verifies** GL ⊢ H ↔ A(H). Also empirically test uniqueness: independent runs / alternative algorithms must yield GL-equivalent outputs.

### 2.3 The iterated-consistency hierarchy, internalized in GL

Define: Con₀ := ¬□⊥; Con_{n+1} := ¬□¬Con_n  (consistency of the base system extended by Con_n, via the formalized deduction theorem □_{F+X}φ ↔ □_F(X→φ)).

**Normal form (unit-test this derivation):** ¬Con_n ≡ □^{n+1}⊥ propositionally implies Con_{n+1} = ¬□¬Con_n ≡ ¬□(□^{n+1}⊥) = ¬□^{n+2}⊥. By induction:

**Con_n ≡ ¬□^{n+1}⊥.**

The whole transfinite-progression idea (Turing 1939; Feferman 1962) appears at the GL level as the **letterless hierarchy** ¬□⊥, ¬□²⊥, ¬□³⊥, …

**Target theorems (machine-check both):**

- **(Monotone)** For all n: GL ⊢ Con_{n+1} → Con_n.  (From derivable □A→□□A.)
- **(Strict)** For all n: GL ⊬ Con_n → Con_{n+1}, equivalently GL ⊬ □^{n+2}⊥ → □^{n+1}⊥. **Each non-derivability must be witnessed by an explicit finite countermodel artifact.**

**KAT for (Strict), n=0:** linear irreflexive 2-chain x → t (t terminal). At t: □⊥ holds vacuously. At x: □²⊥ holds (all successors satisfy □⊥) but □⊥ fails (t ⊭ ⊥). So x ⊨ □²⊥ ∧ ¬□⊥, refuting □²⊥→□⊥. **Prediction:** the minimal countermodel for stage n is the linear (n+2)-chain — minimal-size verification by exhaustive search for small n is part of E-A2. Depth grows linearly with n: *the witness that the hierarchy hasn’t collapsed at stage n requires a strictly deeper world-structure.* This is the quantitative face of “generativity.”

Also machine-check the classical second-incompleteness shape: GL ⊢ ¬□⊥ → ¬□¬□⊥.

**Measurement space:** the **letterless fragment** of GL is completely classified (every letterless formula is GL-equivalent to a Boolean combination of □^n⊥ — normal form theorem, Boolos 1993). Growth claims made inside this fragment are therefore *exact*, not sampling artifacts. Implement the letterless normal-form reducer; it is the clean ruler for “what is new at stage n.”

### 2.4 LP (Logic of Paradox; Priest 1979; antecedent Asenjo 1966)

- **Values:** {t, b, f}, order f < b < t. **Designated:** {t, b}.
- **Tables:** ¬(t)=f, ¬(b)=b, ¬(f)=t; ∧ = min; ∨ = max; A→B := ¬A∨B.
- **Consequence:** Γ ⊨_LP φ iff every valuation designating all of Γ designates φ.
- **Known facts to exhibit:**
  - Non-explosion: λ∧¬λ ⊭_LP B  (witness: v(λ)=b, v(B)=f).
  - Liar constraint satisfiable: v(λ)=b designates λ↔¬λ (value b).
  - **MP fails:** A, A→B ⊭_LP B (v(A)=b, v(B)=f). **Disjunctive syllogism fails:** A∨B, ¬A ⊭_LP B (same family).
  - **Conservativity (inertness) lemma:** for λ-free B: T, λ∧¬λ ⊨_LP B iff T ⊨_LP B. (Proof sketch for the README: any valuation separating T from B extends with v(λ)=b. Verify by exhaustive enumeration for languages of ≤ 4 atoms: 3⁴ valuations — trivial.)
- Classical environment = same machinery with values {t,f}: liar constraint unsatisfiable ⇒ vacuous explosion (λ↔¬λ ⊨_cl B for every B).

### 2.5 Honesty notes for all write-ups

- Arithmetic reading of §2.3 (PA + Con_n ⊬ Con_{n+1}) carries standard soundness caveats (e.g., consistency/1-consistency of the base). At the GL level the statements are unconditional and decidable — one reason we work there.
- Solovay’s theorem is cited, not re-proved. We operate purely at the modal level.

-----

## 3. Experiments

### E-A1 — Fixed-point engine (diagonalization as computation)

Input: modalized A(p). Output: H + machine-checked certificate GL ⊢ H ↔ A(H).

- Pass all KATs (§2.2 table).
- Random battery: generate ≥ 200 random modalized A(p) (modal depth ≤ 3, ≤ 2 extra atoms); compute and verify all fixed points; test uniqueness pairwise where multiple algorithms/runs available.
- **Paper mapping:** §3 (the diagonal lemma as a *construction*, not a paradox-trick); §M (self-specification by constraint = fixed point).

### E-A2 — The hierarchy (generation, quantified)

For n = 0…N (N ≥ 8):

- Verify GL ⊢ Con_{n+1} → Con_n (prover certificate).
- Refute GL ⊢ Con_n → Con_{n+1}: produce explicit finite countermodel artifact (JSON + rendered tree SVG); verify the §2.3 KAT at n=0; empirically confirm minimal countermodel = (n+2)-chain for n ≤ 4 by exhaustive search.
- Letterless normal-form reducer: at each stage n, compute the set of newly available letterless truths (relative to the fragment classification); plot growth.
- **Output figure:** “the ladder” — hierarchy stage vs. minimal witnessing depth (linear, unbounded).
- **Paper mapping:** §3/§8 (Turing–Feferman generative lineage); 「作られたものから作るものへ」 — each completed stage (the made) defines the next transcendence (the making).

### E-A3 — Internal control: the active ingredient is the *negative* self-reference (the gap)

Within GL itself, contrast:

- Gödel-type seed (fixed point of ¬□p) → ¬□⊥ → launches E-A2’s hierarchy.
- **Henkin-type seed** (fixed point of □p) → ⊤ → F + ⊤ = F. **Flatline.**
  Same diagonal operator; the only difference is the negation — the gap between the self-referring and the referred. Positive self-endorsement generates nothing; the determiner/determined **gap** is the engine.
- **Paper mapping:** §4 feature table (“contradiction as condition of creativity” row) — this is its direct computational correlate. Also pre-empts the triviality objection (§5 below).

### E-B1 — Classical explosion exhibit

Semantic route: show λ↔¬λ classically unsatisfiable; hence λ↔¬λ ⊨_cl B for arbitrary B (vacuously). Emit the enumeration artifact.

### E-B2 — LP quarantine exhibit (inertness)

- Satisfiability of the liar constraint (valuation artifact).
- Conservativity check: enumerate languages up to 4 atoms; verify T, λ∧¬λ ⊨_LP B ⇔ T ⊨_LP B for all λ-free B; for a small fixed T, compute Th_LP before/after — **zero growth** (the flatline figure).
- MP and DS failure witnesses (valuation artifacts): quarantine’s price is inferential power.
- **Paper mapping:** §5 (against the dialetheist reading): a contained contradiction *does no work*.

### E-C (optional / stretch; separate WP, do not block)

- **C1:** Kripke-style fixed-point model for a transparent truth predicate over LP / strong-Kleene on a small fragment (liar gets b in the minimal fixed point) — first-order upgrade of E-B2.
- **C2:** Arithmetic-level single iteration F → F+Con(F) using an **existing** incompleteness formalization (Isabelle/HOL: Paulson 2015; Lean 4 community libraries — agents verify current availability). **Do NOT re-formalize incompleteness from scratch.** Deliverable: one machine-checked instance of “new theorem at stage 1.”

-----

## 4. Metrics & threats to validity (read before designing; encode in README)

1. **Triviality objection** (“adding axioms always proves more”). Answers built into the design: (a) the added axiom is **self-generated** — Con(F) is computed *by the diagonal engine from the system’s own provability structure*, not imported; (b) E-A3: the Henkin seed goes through the *same* engine and generates **nothing** — so it is not “adding axioms” that generates, but the specific gap-structure of the seed.
1. **Cross-logic comparison is structural, not numeric.** Do not compare raw theorem counts between GL and LP (different languages/logics). The honest claim: *the same diagonal seed launches a strict unbounded hierarchy in one environment and provably nothing in the others.* State it exactly this way.
1. **Exactness of growth claims:** confine growth measurement to the letterless fragment (completely classified ⇒ no sampling bias).
1. **Epistemic status:** illustration, not proof, of the philosophical thesis. Mandatory sentence in every README/abstract.

-----

## 5. Work packages (parallelizable across agents)

|WP     |Content                                                                                                                                   |Depends on     |Definition of Done                                                                                                                                                                    |
|-------|------------------------------------------------------------------------------------------------------------------------------------------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**WP1**|GL core: formula AST/parser/printer; GL prover (tableau **and** finite-Kripke search — two methods, cross-checked); countermodel extractor|—              |Both methods agree on a 1,000-formula random suite + all §2 KATs; no formula both proved & refuted; countermodels machine-validated (transitive, irreflexive, formula refuted at root)|
|**WP2**|Fixed-point engine (Boolos 1993 algorithm; optionally a second algorithm for cross-check)                                                 |WP1            |All §2.2 KATs; 200-formula battery verified; uniqueness checks pass                                                                                                                   |
|**WP3**|E-A2 + E-A3 experiments; letterless normal-form reducer; ladder figure                                                                    |WP1, WP2       |(Monotone)/(Strict) certified for n ≤ 8; minimality confirmed n ≤ 4; figures emitted                                                                                                  |
|**WP4**|LP + classical engines; E-B1, E-B2                                                                                                        |— (independent)|Enumeration complete ≤ 4 atoms; conservativity verified; MP/DS witnesses emitted; flatline figure                                                                                     |
|**WP5**|Integration: headline table (§1) auto-generated from artifacts; repo packaging, manifest, CI, Zenodo-ready metadata                       |WP1–4          |Single-command full reproduction; manifest lists every claim → artifact path                                                                                                          |
|**WP6**|Optional: E-C1, E-C2                                                                                                                      |WP5            |One machine-checked instance each; clearly marked optional                                                                                                                            |

**Priority order:** WP1 → WP2 → WP3; WP4 parallel from day one; WP5 last; WP6 only if time remains.

-----

## 6. Interfaces (shared across agents — do not deviate)

**Formula JSON:**

```json
{"type":"bot"} | {"type":"atom","name":"p"} | {"type":"not","arg":F}
| {"type":"and","args":[F,...]} | {"type":"or","args":[F,...]}
| {"type":"imp","left":F,"right":F} | {"type":"iff","left":F,"right":F}
| {"type":"box","arg":F}
```

**Kripke model JSON:**

```json
{"worlds":[0,1,...], "rel":[[0,1],...], "val":{"p":[1,...]},
 "refutes":{"formula":F, "at":0},
 "checks":{"transitive":true,"irreflexive":true}}
```

**Claim manifest (WP5 collates):** every result line = `{claim, status: proved|refuted, certificate_or_countermodel: path, experiment: id}`.

**Language:** agents’ choice (Python 3.12 recommended for velocity; Rust acceptable). All inter-WP communication via the JSON schemas. Property-based testing encouraged (hypothesis / proptest).
**Performance:** formulas are tiny; GL decidability via finite model property — search depth bounded by modal depth. Naive implementations suffice; correctness over speed.

-----

## 7. Verification discipline & forbidden claims (binding)

- **Every** claimed theorem carries a prover certificate; **every** claimed non-theorem carries a validated countermodel. No unverified outputs anywhere, including figures.
- Two independent methods cross-checked wherever feasible (two provers; two fixed-point algorithms).
- **Forbidden in any agent-generated text:** (1) “proves the philosophical thesis”; (2) “Nishida anticipated Gödel” as a historical claim; (3) novelty claims about the mathematics (it is all known; the contribution is the verified exhibit and its design); (4) causal-eliminativist generalizations — constraint/fixed-point vocabulary is used for describing the constructions only (see paper §M scope limits).
- Citation diction in docs follows the paper’s standing rule (default: “consistent with / converges with / provides formal support for”; “building on/following” reserved for Nishida and the author’s own work).

-----

## 8. Deliverables

1. Repository (Zenodo-ready: README, CITATION.cff, license, manifest, CI).
1. Artifacts: all certificates + countermodels (JSON), rendered trees (SVG).
1. Figures: (i) headline one-seed-three-environments table; (ii) the ladder (stage vs. minimal witness depth); (iii) flatline (LP theorem-set before/after); (iv) E-A3 Gödel-vs-Henkin contrast.
1. `RESULTS.md`: claim-by-claim with artifact links, in the §4 metric language.
1. Author/credit block per paper rule: **Franny Philos Sophia** (Elanare Institute).

## 9. Expected results (falsifiable predictions — deviations are bugs or findings; report either way)

- All §2.2 KATs reproduce. Fixed points unique up to GL-equivalence across methods.
- (Monotone) holds and (Strict) fails-to-derive at every tested stage; minimal countermodels are the (n+2)-chains for n ≤ 4.
- GL ⊢ ¬□⊥ → ¬□¬□⊥ certified.
- LP: liar satisfiable at b; zero λ-free growth; MP/DS counterexamples found.
- Classical: liar unsatisfiable; vacuous explosion confirmed by enumeration.

## 10. References (implementation-relevant)

Gödel (1931). Turing, “Systems of Logic Based on Ordinals” (1939). Feferman, “Transfinite Recursive Progressions of Axiomatic Theories,” *JSL* 27 (1962). Segerberg, *An Essay in Classical Modal Logic* (1971). Solovay, “Provability Interpretations of Modal Logic,” *Israel J. Math.* 25 (1976). Smoryński, *Self-Reference and Modal Logic* (1985). **Boolos, *The Logic of Provability* (1993)** — primary implementation reference (fixed-point algorithms; letterless normal form). Priest, “The Logic of Paradox,” *JPL* 8 (1979). Asenjo, “A Calculus of Antinomies,” *NDJFL* (1966). Franzén, *Gödel’s Theorem: An Incomplete Guide to Its Use and Abuse* (2005) — tone-setting for all write-ups. Paulson, Isabelle/HOL incompleteness formalization (2015) — WP6 only.