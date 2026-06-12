# RESULTS

## Requested command

Command attempted from the artifact root in this sandbox:

```bash
cd /mnt/data/T3_con_n_normal_form_v2
uv run pytest -q
```

Observed result in this sandbox:

```text
3 errors during collection
ModuleNotFoundError: No module named 'gl'
```

This sandbox contains only the T3 artifact tree, not the repository top with `src/gl` / the installable `gl` package. Therefore I cannot honestly report the requested full-repository `X passed` value here.

## Checks completed in this sandbox

```bash
python -m py_compile \
  tests/test_con_n_normal_form.py \
  tests/test_con_n_monotone.py \
  tests/test_con_n_strict.py \
  experiments/wp3/build_countermodels.py
```

Result: passed.

Additional JSON sanity checks completed for `strict_n0.json` through `strict_n4.json`:

- `worlds == list(range(n + 2))`
- `rel == [[i, j] for i < j]`, with transitive closure included explicitly
- `val == {}`
- `refutes.at == 0`
- `checks == {"transitive": true, "irreflexive": true}`
- the serialized `refutes.formula` is false at world `0` under the included frame semantics

Result: passed.

## Command to run in the actual repository

From the repository top, after placing this artifact tree over the repo:

```bash
uv run python experiments/wp3/build_countermodels.py
uv run pytest -q
```

Expected new test count contributed by this artifact:

- `test_con_n_normal_form.py`: 9 parametrized cases
- `test_con_n_monotone.py`: 9 parametrized cases
- `test_con_n_strict.py`: 15 parametrized cases
- total new cases: 33

The reviewer's baseline says the repository already has 26 tests, so the expected full total is 59 tests if no other tests have changed.
