# T2 fixed-point engine revision results

## Summary

This revision contains the requested code changes, but the full repository test run could not be completed in this ChatGPT sandbox because the target repository files are not present here.

Available in this sandbox:

- previous generated zip only: `/mnt/data/T2_fixed_point_chatgpt.zip`
- no target `pyproject.toml`
- no target `src/gl/formula.py`
- no target `src/gl/tableau.py`
- no target `src/gl/kripke_search.py`
- no installed `hypothesis` in the isolated working directory used by `uv run`

Therefore I cannot honestly report `X passed` for the integrated repository. The attempted command and failure mode are recorded below and in `pytest_attempt.log`.

## Actual command attempted in this sandbox

```bash
cd /mnt/data/T2_revised/T2_fixed_point_chatgpt
uv run pytest -q
```

Result: collection failed before tests could run.

Relevant error:

```text
ModuleNotFoundError: No module named 'gl'
ModuleNotFoundError: No module named 'hypothesis'
3 errors during collection
```

A syntax-only check was possible and passed:

```bash
python -m py_compile $(find /mnt/data/T2_revised/T2_fixed_point_chatgpt -name '*.py')
```

## Expected pytest item count in the target repository

The added tests define 10 pytest items:

- `tests/test_fixed_point_kats.py`: 7 items
  - engine/prover import separation check
  - modalized rejection check
  - Henkin no-simplifier boundary check
  - 4 known-answer tests
- `tests/test_fixed_point_random.py`: 1 Hypothesis item with `max_examples=225`
- `tests/test_fixed_point_uniqueness.py`: 2 items
  - known-answer main/alt equivalence
  - Hypothesis item with `max_examples=225`

Given the stated existing 26 passing tests in the integration repository, the expected pytest item total is 36 if all new items pass. Internally, Hypothesis is configured to consume 225 generated examples for the fixed-point equation battery and 225 generated examples for main/alt equivalence, for 450 generated examples total across the two Hypothesis tests.

## Response to item 2: `_simplify` boundary

The simplifier was reduced.

Kept:

- Boolean constant folding involving explicit `Top = Not(bot())` and `bot()`
- `Box(Top) -> Top`
- neutral constant elimination for `And`, `Or`, `Imp(Top, X)`, `Imp(bot, X)`, `Imp(X, Top)`, `Iff(Top, X)`, `Iff(X, Top)`

Removed from the previous submission:

- double-negation elimination
- `Imp(X, bot) -> Not(X)`
- `Imp(X, X) -> Top`
- `Iff(X, X) -> Top`
- `Iff(bot, X) -> Not(X)` / `Iff(X, bot) -> Not(X)`
- associative flattening of nested `And` / `Or`

The production `fixed_point.py` docstring now explicitly states this normalization boundary.

A new test was added:

```python
def test_henkin_without_simplifier_returns_box_top_and_prover_equiv(monkeypatch):
    monkeypatch.setattr(fixed_point_module, "_simplify", lambda f: f)
    H = fixed_point_module.fixed_point(Box(atom("p")), "p")
    assert H == Box(Not(bot()))
    assert prove_gl(Iff(H, Not(bot()))).status == "proved"
```

By direct trace of the algorithm, with `_simplify` disabled, `fixed_point(Box(atom("p")), "p")` returns `Box(Not(bot()))`, i.e. `□⊤`. The independent-prover equivalence check is present in the test, but it could not be executed in this sandbox because the target prover module is absent.

## Response to item 3: alt independence

A truly separate rank/trace-based fixed-point engine was not implemented in this revision. The reason is that the most straightforward independent alternative, bounded candidate search via Bernardi uniqueness, would call `prove_gl` inside the engine and would violate the engine/prover separation requirement.

`fixed_point_alt.py` remains path-based and still depends on the same k-decomposition theorem as the main implementation. Its docstring now says this explicitly: the uniqueness tests are a structural-difference sanity check, not a fully independent second proof procedure.

## Response to item 4: random battery scale

The random battery remains above the requested threshold:

- fixed-point equation battery: `max_examples=225`
- main/alt equivalence battery: `max_examples=225`

The generator guarantees modalized formulas by construction, not by post-generation filtering. It tracks whether the current position is under a `Box` and only offers `atom("p")` when that flag is true. The generator bounds modal nesting with `boxes_left=3`; the tests also assert `modal_depth(A) <= 3`.

Actual runtime and actual consumed-example count could not be measured in this sandbox because the target repository and dependency environment are unavailable here.

## Response to item 5: existing tests impact

The integrated repository's existing 26 tests could not be run here because the repository is not present in this sandbox. The included new test count is 10 pytest items. If the integration repository still has 26 existing passing tests and all new items pass, the expected total would be 36 passed.

## Files changed from the previous zip

- `src/gl/fixed_point.py`
  - simplifier reduced
  - docstring clarified
- `src/gl/fixed_point_alt.py`
  - simplifier reduced
  - docstring clarified about non-independence
- `tests/test_fixed_point_kats.py`
  - added no-simplifier Henkin boundary test
  - strengthened AST import-separation check to reject imported `prove_gl` names in engine modules
- `tests/test_fixed_point_random.py`
  - added `RANDOM_EXAMPLES = 225`
  - added `HealthCheck.too_slow` suppression for prover-heavy runs
- `tests/test_fixed_point_uniqueness.py`
  - added `RANDOM_EXAMPLES = 225`
  - added `HealthCheck.too_slow` suppression for prover-heavy runs
- `RESULTS.md`
  - this report
- `pytest_attempt.log`
  - local failed collection attempt from this sandbox
