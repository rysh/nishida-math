# S2 letterless normal form reducer v2 results

## Summary

- `src/gl/letterless.py` was simplified to match the repository's fixed `Formula` schema directly.
- Removed the previous generic compatibility layer: `_mapping_view`, `_field`, `_normal_kind`, `_unary_child`, `_binary_children`, `_nary_children`, `_as_sequence`, and alias dispatch are gone.
- Public API remains unchanged:
  - `is_letterless(F)`
  - `letterless_normal_form(F)`
  - `nf_equiv(F1, F2)`
- `letterless.py` does not import `gl.tableau` or `gl.kripke_search`; `tests/test_letterless_kats.py` includes an AST check for this separation.

## Test execution status

Target command requested:

```bash
uv run pytest -q
```

I attempted to run this command in the artifact directory available in this container:

```bash
cd /mnt/data/S2_letterless_normal_form_v2 && uv run pytest -q
```

This container does not contain the full target repository. It contains only the generated artifact files, not the repository `pyproject.toml`, `src/gl/formula.py`, `src/gl/tableau.py`, or the pre-existing 26 tests. The command therefore failed at collection time:

```text
ModuleNotFoundError: No module named 'gl'
ModuleNotFoundError: No module named 'hypothesis'
2 errors during collection
```

I therefore do **not** claim an actual integrated `X passed` result here. The expected integrated pytest item count, assuming the repository's existing 26 tests remain unchanged, is:

```text
26 existing tests + 15 new tests = 41 pytest items
```

The `15` new items are:

```text
14 tests in tests/test_letterless_kats.py
 1 test in tests/test_letterless_random.py, with 500 Hypothesis examples
```

Local syntax/schema checks performed in this container:

```bash
python -m py_compile \
  src/gl/letterless.py \
  tests/test_letterless_kats.py \
  tests/test_letterless_random.py
```

Result:

```text
passed
```

I also ran a small local schema-compatible smoke check using a temporary `Formula` stub matching the provided dataclass fields. This confirmed canonical outputs for the dispatch KATs, including the corrected row. This was not the repository prover and is not counted as an integrated GL proof result.

## Corrected dispatch KAT row

The original dispatch KAT table contained this row:

```python
Not(Box(Not(Box(bot()))))  ->  Not(box_power(bot(), 2))
```

The correct expected normal form is:

```python
Not(Box(Not(Box(bot()))))  ->  Not(box_power(bot(), 1))
```

Mathematical reason, in brief:

```text
Not(Box(bot())) is propositionally equivalent to Imp(Box(bot()), bot()).
Therefore Box(Not(Box(bot()))) is GL-equivalent to Box(Imp(Box(bot()), bot())).
By the Löb instance □(□⊥ → ⊥) → □⊥, together with the trivial converse
□⊥ → □(□⊥ → ⊥), this reduces to □⊥ = box_power(bot(), 1).
Negating both sides gives Not(Box(Not(Box(bot())))) ≡ Not(box_power(bot(), 1)).
```

The nearby formula whose expected normal form is `Not(box_power(bot(), 2))` is instead:

```python
Not(Box(Box(bot())))
```

## Notes for integration

Run the actual integrated test from repository top:

```bash
uv run pytest -q
```

If all existing tests remain at 26 and the new tests are collected as above, the expected success line is:

```text
41 passed
```
