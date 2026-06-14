# Generative Contradiction — A Computational Exhibit

[![DOI](https://zenodo.org/badge/1269017597.svg)](https://doi.org/10.5281/zenodo.20687363)

> **Epistemic status: illustration, not proof, of the philosophical thesis.**
> The underlying mathematics is known (Solovay 1976; de Jongh–Sambin;
> Boolos 1993; Priest 1979). The contribution of this repository is
> demonstration, verification, and artifacts — machine-checked proofs,
> explicit countermodels, and figures.

## Headline

> *The same diagonal seed launches a strict unbounded hierarchy in one
> environment and provably nothing in the others.*

The seed is the same self-referential diagonal in every row:

| Environment | What the seed does | Generativity |
|---|---|---|
| **Classical propositional logic** | the liar `λ ↔ ¬λ` is unsatisfiable; vacuous explosion confirmed by enumeration | **destroyed** (everything follows, nothing distinguishable) |
| **LP** (Priest's Logic of Paradox) | the liar is satisfiable at `v(λ)=b`; exhaustive comparison shows zero new λ-free consequences | **zero** (quarantined, inert) |
| **GL** (Gödel–Löb provability logic) | each `Con_{n+1} → Con_n` is proved; each `Con_n → Con_{n+1}` is refuted by a verified `(n+2)`-chain countermodel | **unbounded** (linear `n+2`) |

The auto-generated rendering of this row-set is at
[`experiments/wp5/artifacts/headline_table.md`](experiments/wp5/artifacts/headline_table.md)
and as an SVG at
[`experiments/wp5/artifacts/headline_figure.svg`](experiments/wp5/artifacts/headline_figure.svg).
A claim-by-claim view with artifact paths is in
[`RESULTS.md`](RESULTS.md).

## Reproduce in one command

Requires [`uv`](https://docs.astral.sh/uv/) and Python 3.12.

```bash
make all
```

This is equivalent to running the CI workflow
[`.github/workflows/test.yml`](.github/workflows/test.yml). It will:

1. `uv sync` — install pinned dependencies from `uv.lock`.
2. `uv run pytest -q` — run the 136-test suite.
3. Regenerate every experiment artifact (WP3 ladder, WP4 classical / LP
   evaluators, WP5 headline table / figure).
4. `git diff --exit-code` — assert no artifact drifted. SVGs and the
   `claims.json` manifest are generated deterministically; any byte
   change fails the build.

If you prefer the raw commands:

```bash
uv sync
uv run pytest -q
uv run python experiments/wp3/build_countermodels.py
uv run python experiments/wp3/build_ladder.py
uv run python experiments/wp3/build_figure.py
uv run python experiments/wp4/e_b1_classical_explosion.py
uv run python experiments/wp4/e_b2_lp_quarantine.py
uv run python experiments/wp5/build_claims.py
uv run python experiments/wp5/build_table.py
uv run python experiments/wp5/build_figure.py
git diff --exit-code
```

## Repository map

```
src/
  gl/                # GL formula AST, tableau prover, finite-Kripke search,
                     # countermodel verifier, fixed-point engine, letterless
                     # normal form. The verifier is import-isolated from the
                     # prover (AST check enforced by the test suite).
  lp/                # Three-valued LP evaluator and entailment.
  classical/         # Classical two-valued evaluator and entailment.
experiments/
  wp3/               # Con_n hierarchy: ladder manifest + figure SVG + per-stage
                     # countermodels (minimality exhaustively verified for n ≤ 4).
  wp4/               # E-B1 classical explosion, E-B2 LP quarantine.
  wp5/               # Headline integration: claims.json (single source of truth)
                     # + headline_table.md + headline_figure.svg.
tests/               # 136 pytest tests; see Makefile target `test`.
docs/
  integration_notes/ # Per-WP design / decision notes.
  con_n_normal_form.md
prompts/             # Triangulate prompts used during construction (3-LLM
                     # workflow). Not required for reproduction.
.github/workflows/   # CI: pytest + artifact regeneration + git diff --exit-code.
02 simspec kether nishida.md   # The simulation spec (not modified).
RESULTS.md           # Claim-by-claim manifest with artifact paths.
```

## Threats to validity

These come from §4 of the simulation spec and are encoded in the design.

1. **Triviality objection** ("adding axioms always proves more"). `Con_n`
   is *self-generated*: the diagonal engine computes it from the system's
   own provability structure (see `src/gl/formula.py:con` and
   `box_power`). It is not an imported axiom. The Henkin contrast that
   sharpens this answer further by showing the same engine generates
   *nothing* from a Henkin seed (referred to as E-A3 in the spec) is **not
   implemented** in this repository; the contrast is referenced from
   Boolos 1993 and listed as out of scope here.

2. **Cross-logic comparison is structural, not numeric.** Theorem counts
   are not compared between GL and LP; the languages and logics differ.
   The honest claim is the headline above.

3. **Exactness of growth claims is confined to the letterless fragment.**
   The letterless fragment is completely classified, so there is no
   sampling bias because there is no sample.

4. **Illustration, not proof.** Restated here so it cannot be missed.

## Citation

If you use this software, please cite it via the
[`CITATION.cff`](CITATION.cff) entry. Archived on Zenodo with concept
DOI [10.5281/zenodo.20687363](https://doi.org/10.5281/zenodo.20687363)
(the concept DOI always resolves to the latest version; individual
released versions have their own DOIs). The associated paper is in
preparation.

## Author

**Franny Philos Sophia** (Elanare Institute), per §8 of the simulation
spec.

- ORCID: <https://orcid.org/0009-0004-7089-5265>
- Contact: <frany.philos.sophia@elanare.jp>
- Repository: <https://github.com/rysh/nishida-math>

## License

[MIT](LICENSE). See `LICENSE` for the full text.

## References (implementation-relevant)

- R. M. Solovay, *Provability interpretations of modal logic*,
  Israel J. Math. **25** (1976).
- G. Boolos, *The Logic of Provability* (Cambridge University Press,
  1993). Primary implementation reference for the fixed-point algorithm
  and the letterless normal form.
- G. Priest, *The Logic of Paradox*, J. Philos. Logic **8** (1979).
- F. L. G. Asenjo, *A Calculus of Antinomies*,
  Notre Dame J. Formal Logic (1966).
- T. Franzén, *Gödel's Theorem: An Incomplete Guide to Its Use and
  Abuse* (A K Peters, 2005) — tone-setting for write-ups.
