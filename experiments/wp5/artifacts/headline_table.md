# Headline: ONE SEED, THREE ENVIRONMENTS

*Auto-generated from `experiments/wp5/artifacts/claims.json`. Do not edit by hand; run `uv run python experiments/wp5/build_table.py` to regenerate.*

| Environment | Contradiction status | What follows from the seed | Formal witness | Generativity |
|---|---|---|---|---|
| Classical propositional logic | explodes | everything (vacuous entailment) | [E-B1](experiments/wp4/artifacts/e_b1_classical_explosion.json) — `satisfiable: false`, `vacuous_explosion: true`, all 5 sample vacuity checks pass ([details](experiments/wp4/artifacts/e_b1_classical_explosion_details.json)) | destroyed (everything derivable, nothing distinguishable) |
| LP (Priest's Logic of Paradox) | tolerated | nothing new in the λ-free language (inert) | [E-B2](experiments/wp4/artifacts/e_b2_lp_quarantine.json) — `satisfiable: true`, `inert: true`, MP fails at v(A)=b, v(B)=f; DS fails at v(A)=b, v(B)=f ([details](experiments/wp4/artifacts/e_b2_lp_quarantine_details.json)) | zero (contradiction quarantined, no new λ-free consequences) |
| GL (Gödel-Löb provability logic) | resolved by ascent | a strictly higher consistency level (Con_n ⊊ Con_{n+1}) | [E-A2](experiments/wp3/artifacts/ladder_manifest.json) — stages 0..8, every stage's monotone direction proved and strict direction refuted, witness counts [2, 3, 4, 5, 6, 7, 8, 9, 10] (linear n+2); minimality exhaustively verified for n ∈ [0, 1, 2, 3, 4, 5] | unbounded (each stage requires a strictly deeper frame; linear n+2) |

## Reading

- **Contradiction status**: how each environment treats the contradiction the seed produces.
- **What follows from the seed**: what is derivable from the contradiction in that environment.
- **Formal witness**: the machine-checked artifact backing the row. Each link resolves to a JSON artifact in the repository.
- **Generativity**: the unifying axis. Classical destroys distinction (everything follows, nothing can be told apart); LP quarantines the contradiction but generates nothing new in the λ-free fragment; only GL turns the contradiction into the engine of a strictly increasing hierarchy. This is the computational counterpart of Paper A's three modes of contradiction (classical / tolerative / generative).

## Source

Generated from `experiments/wp5/artifacts/claims.json`, which is itself built by `experiments/wp5/build_claims.py` against the three input artifacts listed under each row's `formal_witness`.
