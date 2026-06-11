## §0 自己申告

* **確信度**：High
* **不安な箇所**

  1. **E-B2 inertness の「任意の小 T と λ-free B」**は無限全式ではなく、実験 artifact として有限 bounded suite に落としています。実装では 4 atoms、110 個の λ-free formulas、premise set size ≤ 2、81 base valuations / 243 full valuations で違反ゼロを確認します。
  2. **`And()` / `Or()` の空引数**は標準的に `And() = t`, `Or() = f` として実装しました。既存 `gl.formula.And/Or` が空引数を許すかは未確認です。
  3. **artifact JSON の主ファイル**は指定されたキーだけにし、詳細列挙は `_details.json` に分けました。検証側が単一 JSON に enumeration まで要求する場合は統合が必要です。
  4. **MP / DS failure witness の最小性**は主張していません。指定通り `v(A)=b, v(B)=f` を witness として出しています。
* **参照した文献・URL**：なし。今回の実装は提示仕様のみに基づいています。
* **ハルシネーション可能性が高い記述**：LP / classical の数学的背景について外部文献由来の主張は入れていません。唯一の注意点は、E-B2 の inertness を「有限 bounded enumeration artifact」として扱っている点です。これは proof ではなく illustration / executable check です。

ZIP も作成済みです：
[Download S1_lp_classical_evaluator.zip](sandbox:/mnt/data/S1_lp_classical_evaluator.zip)

---

## `src/lp/evaluator.py`

```python
# src/lp/evaluator.py
from __future__ import annotations

from typing import Literal, Mapping, TypeAlias

from gl.formula import Formula

Lit: TypeAlias = Literal["t", "b", "f"]

DESIGNATED: frozenset[Lit] = frozenset({"t", "b"})
_LIT_ORDER: dict[Lit, int] = {"f": 0, "b": 1, "t": 2}
_ORDER_LIT: dict[int, Lit] = {0: "f", 1: "b", 2: "t"}


def _require_unary(formula: Formula) -> Formula:
    if formula.arg is None:
        raise ValueError(f"malformed unary formula: {formula!r}")
    return formula.arg


def _require_binary(formula: Formula) -> tuple[Formula, Formula]:
    if formula.left is None or formula.right is None:
        raise ValueError(f"malformed binary formula: {formula!r}")
    return formula.left, formula.right


def neg_lit(value: Lit) -> Lit:
    """Priest LP negation: ¬t=f, ¬b=b, ¬f=t."""
    if value == "t":
        return "f"
    if value == "b":
        return "b"
    if value == "f":
        return "t"
    raise ValueError(f"unknown LP literal: {value!r}")


def and_lit(left: Lit, right: Lit) -> Lit:
    """LP conjunction as min under f < b < t."""
    return _ORDER_LIT[min(_LIT_ORDER[left], _LIT_ORDER[right])]


def or_lit(left: Lit, right: Lit) -> Lit:
    """LP disjunction as max under f < b < t."""
    return _ORDER_LIT[max(_LIT_ORDER[left], _LIT_ORDER[right])]


def imp_lit(left: Lit, right: Lit) -> Lit:
    """LP material implication A → B := ¬A ∨ B."""
    return or_lit(neg_lit(left), right)


def iff_lit(left: Lit, right: Lit) -> Lit:
    """LP biconditional A ↔ B := (A → B) ∧ (B → A)."""
    return and_lit(imp_lit(left, right), imp_lit(right, left))


def evaluate_lp(formula: Formula, valuation: Mapping[str, Lit]) -> Lit:
    """Evaluate a Formula in Priest's Logic of Paradox.

    Formula values are ``"t"``, ``"b"``, and ``"f"``.  Any occurrence of
    ``type == "box"`` is rejected because the LP evaluator is intentionally
    non-modal.
    """
    match formula.type:
        case "box":
            raise ValueError("LP evaluator does not accept modal formulas containing box")
        case "bot":
            return "f"
        case "atom":
            if formula.name is None:
                raise ValueError(f"malformed atom formula: {formula!r}")
            value = valuation[formula.name]
            if value not in DESIGNATED and value != "f":
                raise ValueError(f"unknown LP literal for atom {formula.name!r}: {value!r}")
            return value
        case "not":
            return neg_lit(evaluate_lp(_require_unary(formula), valuation))
        case "and":
            value: Lit = "t"
            for arg in formula.args:
                value = and_lit(value, evaluate_lp(arg, valuation))
            return value
        case "or":
            value: Lit = "f"
            for arg in formula.args:
                value = or_lit(value, evaluate_lp(arg, valuation))
            return value
        case "imp":
            left, right = _require_binary(formula)
            return imp_lit(evaluate_lp(left, valuation), evaluate_lp(right, valuation))
        case "iff":
            left, right = _require_binary(formula)
            return iff_lit(evaluate_lp(left, valuation), evaluate_lp(right, valuation))
        case _:
            raise ValueError(f"unknown Formula type: {formula.type!r}")
```

---

## `src/lp/entailment.py`

```python
# src/lp/entailment.py
from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import product

from gl.formula import Formula

from lp.evaluator import DESIGNATED, Lit, evaluate_lp

LP_VALUES: tuple[Lit, ...] = ("t", "b", "f")


def all_lp_valuations(atoms: Sequence[str]) -> Iterator[dict[str, Lit]]:
    """Yield all 3^|atoms| LP valuations over the supplied atom order."""
    for values in product(LP_VALUES, repeat=len(atoms)):
        yield dict(zip(atoms, values, strict=True))


def entails_lp(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """Brute-force LP entailment over all 3^|atoms| valuations.

    Γ ⊨_LP φ iff every valuation designating all formulas in Γ also designates φ.
    """
    for valuation in all_lp_valuations(atoms):
        if all(evaluate_lp(premise, valuation) in DESIGNATED for premise in premises):
            if evaluate_lp(conclusion, valuation) not in DESIGNATED:
                return False
    return True
```

---

## `src/classical/evaluator.py`

```python
# src/classical/evaluator.py
from __future__ import annotations

from typing import Mapping

from gl.formula import Formula


def _require_unary(formula: Formula) -> Formula:
    if formula.arg is None:
        raise ValueError(f"malformed unary formula: {formula!r}")
    return formula.arg


def _require_binary(formula: Formula) -> tuple[Formula, Formula]:
    if formula.left is None or formula.right is None:
        raise ValueError(f"malformed binary formula: {formula!r}")
    return formula.left, formula.right


def evaluate_classical(formula: Formula, valuation: Mapping[str, bool]) -> bool:
    """Evaluate a Formula in classical propositional logic.

    This is the two-valued restriction of the non-modal machinery.  Any
    occurrence of ``type == "box"`` is rejected.
    """
    match formula.type:
        case "box":
            raise ValueError("classical evaluator does not accept modal formulas containing box")
        case "bot":
            return False
        case "atom":
            if formula.name is None:
                raise ValueError(f"malformed atom formula: {formula!r}")
            value = valuation[formula.name]
            if not isinstance(value, bool):
                raise ValueError(f"classical valuation for atom {formula.name!r} is not bool: {value!r}")
            return value
        case "not":
            return not evaluate_classical(_require_unary(formula), valuation)
        case "and":
            return all(evaluate_classical(arg, valuation) for arg in formula.args)
        case "or":
            return any(evaluate_classical(arg, valuation) for arg in formula.args)
        case "imp":
            left, right = _require_binary(formula)
            return (not evaluate_classical(left, valuation)) or evaluate_classical(right, valuation)
        case "iff":
            left, right = _require_binary(formula)
            return evaluate_classical(left, valuation) == evaluate_classical(right, valuation)
        case _:
            raise ValueError(f"unknown Formula type: {formula.type!r}")
```

---

## `src/classical/entailment.py`

```python
# src/classical/entailment.py
from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import product

from gl.formula import Formula

from classical.evaluator import evaluate_classical


def all_classical_valuations(atoms: Sequence[str]) -> Iterator[dict[str, bool]]:
    """Yield all 2^|atoms| classical valuations over the supplied atom order."""
    for values in product((False, True), repeat=len(atoms)):
        yield dict(zip(atoms, values, strict=True))


def entails_classical(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """Brute-force classical entailment over all 2^|atoms| valuations."""
    for valuation in all_classical_valuations(atoms):
        if all(evaluate_classical(premise, valuation) for premise in premises):
            if not evaluate_classical(conclusion, valuation):
                return False
    return True
```

---

## `experiments/wp4/e_b1_classical_explosion.py`

```python
# experiments/wp4/e_b1_classical_explosion.py
from __future__ import annotations

import json
from pathlib import Path

from classical.entailment import all_classical_valuations, entails_classical
from classical.evaluator import evaluate_classical
from gl.formula import And, Iff, Not, atom, bot

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SUMMARY_PATH = ARTIFACT_DIR / "e_b1_classical_explosion.json"
DETAILS_PATH = ARTIFACT_DIR / "e_b1_classical_explosion_details.json"


def run() -> dict[str, object]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    lambda_atoms = ["lambda"]

    enumeration = [
        {
            "valuation": valuation,
            "value": evaluate_classical(liar, valuation),
        }
        for valuation in all_classical_valuations(lambda_atoms)
    ]
    satisfiable = any(row["value"] for row in enumeration)

    # Representative conclusions.  Since no valuation satisfies λ↔¬λ, the
    # entailment check is vacuous for every conclusion over the chosen atom set.
    p = atom("p")
    sample_conclusions = [
        bot(),
        p,
        Not(p),
        And(p, Not(p)),
        Iff(lam, Not(lam)),
    ]
    vacuity_checks = [
        entails_classical([liar], conclusion, ["lambda", "p"])
        for conclusion in sample_conclusions
    ]
    vacuous_explosion = (not satisfiable) and all(vacuity_checks)

    summary = {
        "satisfiable": satisfiable,
        "vacuous_explosion": vacuous_explosion,
        "enumeration_size": len(enumeration),
    }
    details = {
        **summary,
        "formula": liar.to_json(),
        "enumeration": enumeration,
        "sample_conclusions": [conclusion.to_json() for conclusion in sample_conclusions],
        "sample_vacuity_checks": vacuity_checks,
    }

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    DETAILS_PATH.write_text(json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
```

---

## `experiments/wp4/e_b2_lp_quarantine.py`

```python
# experiments/wp4/e_b2_lp_quarantine.py
from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Sequence
from itertools import combinations
from pathlib import Path

from gl.formula import And, Formula, Iff, Imp, Not, Or, atom, bot
from lp.entailment import all_lp_valuations, entails_lp
from lp.evaluator import DESIGNATED, Lit, evaluate_lp

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SUMMARY_PATH = ARTIFACT_DIR / "e_b2_lp_quarantine.json"
DETAILS_PATH = ARTIFACT_DIR / "e_b2_lp_quarantine_details.json"

BASE_ATOMS = ["p", "q", "r", "s"]
LAMBDA_ATOM = "lambda"
MAX_PREMISES = 2


def _unique_formulas(formulas: Iterable[Formula]) -> list[Formula]:
    seen: set[Formula] = set()
    result: list[Formula] = []
    for formula in formulas:
        if formula not in seen:
            seen.add(formula)
            result.append(formula)
    return result


def lambda_free_formula_suite(atom_names: Sequence[str]) -> list[Formula]:
    """Finite λ-free suite used by the E-B2 bounded enumeration artifact.

    The suite contains ⊥, each atom, negations of those depth-0 formulas, and
    all binary ∧/∨/→/↔ combinations of the depth-0 formulas.  It is intentionally
    finite: the experiment is an executable bounded artifact, not a proof over
    the infinite formula algebra.
    """
    depth_zero = [bot(), *(atom(name) for name in atom_names)]
    literals = [*depth_zero, *(Not(formula) for formula in depth_zero)]
    binary: list[Formula] = []
    for left in depth_zero:
        for right in depth_zero:
            binary.extend((And(left, right), Or(left, right), Imp(left, right), Iff(left, right)))
    return _unique_formulas([*literals, *binary])


def premise_sets(formulas: Sequence[Formula], max_size: int) -> Iterator[tuple[Formula, ...]]:
    yield ()
    if max_size >= 1:
        for formula in formulas:
            yield (formula,)
    if max_size >= 2:
        yield from combinations(formulas, 2)


def designated_mask(formula: Formula, valuations: Sequence[dict[str, Lit]]) -> int:
    mask = 0
    for index, valuation in enumerate(valuations):
        if evaluate_lp(formula, valuation) in DESIGNATED:
            mask |= 1 << index
    return mask


def entails_by_mask(premise_mask: int, conclusion_mask: int) -> bool:
    return (premise_mask & ~conclusion_mask) == 0


def find_mp_failure() -> dict[str, Lit]:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(a, witness) in DESIGNATED
    assert evaluate_lp(Imp(a, b), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([a, Imp(a, b)], b, ["A", "B"])
    return witness


def find_ds_failure() -> dict[str, Lit]:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(Or(a, b), witness) in DESIGNATED
    assert evaluate_lp(Not(a), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([Or(a, b), Not(a)], b, ["A", "B"])
    return witness


def run_inertness_check() -> dict[str, object]:
    formulas = lambda_free_formula_suite(BASE_ATOMS)
    base_valuations = list(all_lp_valuations(BASE_ATOMS))
    full_atoms = [*BASE_ATOMS, LAMBDA_ATOM]
    full_valuations = list(all_lp_valuations(full_atoms))

    base_all_mask = (1 << len(base_valuations)) - 1
    full_all_mask = (1 << len(full_valuations)) - 1

    base_masks = {formula: designated_mask(formula, base_valuations) for formula in formulas}
    full_masks = {formula: designated_mask(formula, full_valuations) for formula in formulas}

    lam = atom(LAMBDA_ATOM)
    contradiction = And(lam, Not(lam))
    contradiction_mask = designated_mask(contradiction, full_valuations)

    violations: list[dict[str, object]] = []
    premise_set_count = 0
    comparison_count = 0

    for premises in premise_sets(formulas, MAX_PREMISES):
        premise_set_count += 1
        base_premise_mask = base_all_mask
        full_premise_mask = full_all_mask
        for premise in premises:
            base_premise_mask &= base_masks[premise]
            full_premise_mask &= full_masks[premise]

        quarantined_premise_mask = full_premise_mask & contradiction_mask

        for conclusion in formulas:
            comparison_count += 1
            right = entails_by_mask(base_premise_mask, base_masks[conclusion])
            left = entails_by_mask(quarantined_premise_mask, full_masks[conclusion])
            if left != right:
                violations.append(
                    {
                        "premises": [premise.to_json() for premise in premises],
                        "conclusion": conclusion.to_json(),
                        "with_lambda_contradiction": left,
                        "without_lambda_contradiction": right,
                    }
                )
                if len(violations) >= 10:
                    break
        if len(violations) >= 10:
            break

    return {
        "inert": not violations,
        "violations": violations,
        "base_atoms": BASE_ATOMS,
        "formula_count": len(formulas),
        "premise_set_count": premise_set_count,
        "max_premises": MAX_PREMISES,
        "base_valuation_count": len(base_valuations),
        "full_valuation_count": len(full_valuations),
        "comparison_count": comparison_count,
        "lambda_contradiction_designated_full_valuations": contradiction_mask.bit_count(),
    }


def run() -> dict[str, object]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    lam = atom(LAMBDA_ATOM)
    liar = Iff(lam, Not(lam))
    witness: dict[str, Lit] = {LAMBDA_ATOM: "b"}
    liar_value = evaluate_lp(liar, witness)
    satisfiable = liar_value in DESIGNATED

    inertness = run_inertness_check()
    mp_failure = find_mp_failure()
    ds_failure = find_ds_failure()

    summary = {
        "satisfiable": satisfiable,
        "inert": inertness["inert"],
        "mp_failure": mp_failure,
        "ds_failure": ds_failure,
    }
    details = {
        **summary,
        "liar_formula": liar.to_json(),
        "liar_witness": witness,
        "liar_value_at_witness": liar_value,
        "inertness": inertness,
    }

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    DETAILS_PATH.write_text(json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
```

---

## `tests/test_lp.py`

```python
# tests/test_lp.py
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from gl.formula import And, Box, Formula, Iff, Imp, Not, Or, atom, bot
from lp.entailment import all_lp_valuations, entails_lp
from lp.evaluator import DESIGNATED, Lit, evaluate_lp

LP_VALUES: tuple[Lit, ...] = ("t", "b", "f")
ATOM_NAMES = ("p", "q", "r")


def formula_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[Formula]:
    leaves = st.one_of(st.just(bot()), st.sampled_from([atom(name) for name in names]))

    def extend(children: st.SearchStrategy[Formula]) -> st.SearchStrategy[Formula]:
        pairs = st.tuples(children, children)
        return st.one_of(
            children.map(Not),
            pairs.map(lambda pair: And(pair[0], pair[1])),
            pairs.map(lambda pair: Or(pair[0], pair[1])),
            pairs.map(lambda pair: Imp(pair[0], pair[1])),
            pairs.map(lambda pair: Iff(pair[0], pair[1])),
        )

    return st.recursive(leaves, extend, max_leaves=8)


def lp_valuation_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[dict[str, Lit]]:
    return st.fixed_dictionaries({name: st.sampled_from(LP_VALUES) for name in names})


def test_lp_negation_table() -> None:
    p = atom("p")
    assert evaluate_lp(Not(p), {"p": "t"}) == "f"
    assert evaluate_lp(Not(p), {"p": "b"}) == "b"
    assert evaluate_lp(Not(p), {"p": "f"}) == "t"


def test_lp_liar_formula_is_satisfied_at_b_only() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    rows = {
        valuation["lambda"]: evaluate_lp(liar, valuation)
        for valuation in all_lp_valuations(["lambda"])
    }
    assert rows == {"t": "f", "b": "b", "f": "f"}
    assert rows["b"] in DESIGNATED


def test_lp_mp_failure_witness() -> None:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(a, witness) in DESIGNATED
    assert evaluate_lp(Imp(a, b), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([a, Imp(a, b)], b, ["A", "B"])


def test_lp_ds_failure_witness() -> None:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(Or(a, b), witness) in DESIGNATED
    assert evaluate_lp(Not(a), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([Or(a, b), Not(a)], b, ["A", "B"])


def test_lp_rejects_box_even_when_nested() -> None:
    p = atom("p")
    with pytest.raises(ValueError):
        evaluate_lp(Box(p), {"p": "t"})
    with pytest.raises(ValueError):
        evaluate_lp(Not(Box(p)), {"p": "t"})


@given(formula=formula_strategy(), valuation=lp_valuation_strategy())
@settings(max_examples=100)
def test_lp_double_negation_is_value_preserving(formula: Formula, valuation: dict[str, Lit]) -> None:
    assert evaluate_lp(Not(Not(formula)), valuation) == evaluate_lp(formula, valuation)


@given(
    premises=st.lists(formula_strategy(("p", "q")), max_size=2),
    conclusion=formula_strategy(("p", "q")),
)
@settings(max_examples=75)
def test_lp_lambda_contradiction_is_inert_for_lambda_free_formulas(
    premises: list[Formula], conclusion: Formula
) -> None:
    lam = atom("lambda")
    lambda_contradiction = And(lam, Not(lam))
    assert entails_lp(premises + [lambda_contradiction], conclusion, ["p", "q", "lambda"]) == entails_lp(
        premises, conclusion, ["p", "q"]
    )
```

---

## `tests/test_classical.py`

```python
# tests/test_classical.py
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from classical.entailment import all_classical_valuations, entails_classical
from classical.evaluator import evaluate_classical
from gl.formula import And, Box, Formula, Iff, Imp, Not, Or, atom, bot
from lp.evaluator import evaluate_lp

ATOM_NAMES = ("p", "q", "r")


def formula_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[Formula]:
    leaves = st.one_of(st.just(bot()), st.sampled_from([atom(name) for name in names]))

    def extend(children: st.SearchStrategy[Formula]) -> st.SearchStrategy[Formula]:
        pairs = st.tuples(children, children)
        return st.one_of(
            children.map(Not),
            pairs.map(lambda pair: And(pair[0], pair[1])),
            pairs.map(lambda pair: Or(pair[0], pair[1])),
            pairs.map(lambda pair: Imp(pair[0], pair[1])),
            pairs.map(lambda pair: Iff(pair[0], pair[1])),
        )

    return st.recursive(leaves, extend, max_leaves=8)


def bool_valuation_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[dict[str, bool]]:
    return st.fixed_dictionaries({name: st.booleans() for name in names})


def as_lit(value: bool) -> str:
    return "t" if value else "f"


def test_classical_liar_formula_is_false_on_all_two_valuations() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    rows = [evaluate_classical(liar, valuation) for valuation in all_classical_valuations(["lambda"])]
    assert rows == [False, False]


def test_classical_vacuous_explosion_from_unsatisfiable_liar() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    p = atom("p")
    assert entails_classical([liar], p, ["lambda", "p"])
    assert entails_classical([liar], Not(p), ["lambda", "p"])
    assert entails_classical([liar], bot(), ["lambda"])


def test_classical_rejects_box_even_when_nested() -> None:
    p = atom("p")
    with pytest.raises(ValueError):
        evaluate_classical(Box(p), {"p": True})
    with pytest.raises(ValueError):
        evaluate_classical(And(p, Box(p)), {"p": True})


@given(formula=formula_strategy(), valuation=bool_valuation_strategy())
@settings(max_examples=100)
def test_classical_matches_lp_on_two_valued_restriction(
    formula: Formula, valuation: dict[str, bool]
) -> None:
    lp_valuation = {name: as_lit(value) for name, value in valuation.items()}
    assert evaluate_lp(formula, lp_valuation) == as_lit(evaluate_classical(formula, valuation))
```

---

## 生成された主 artifact

`experiments/wp4/artifacts/e_b1_classical_explosion.json`

```json
{
  "enumeration_size": 2,
  "satisfiable": false,
  "vacuous_explosion": true
}
```

`experiments/wp4/artifacts/e_b2_lp_quarantine.json`

```json
{
  "ds_failure": {
    "A": "b",
    "B": "f"
  },
  "inert": true,
  "mp_failure": {
    "A": "b",
    "B": "f"
  },
  "satisfiable": true
}
```

追加で、列挙詳細は次の 2 ファイルに出します。

```text
experiments/wp4/artifacts/e_b1_classical_explosion_details.json
experiments/wp4/artifacts/e_b2_lp_quarantine_details.json
```

E-B2 details の主要カウントは以下です。

```json
{
  "base_valuation_count": 81,
  "full_valuation_count": 243,
  "formula_count": 110,
  "premise_set_count": 6106,
  "comparison_count": 671660,
  "violations": []
}
```

## 自己検証結果

提示された `gl.formula` API と互換の最小 stub を置いた一時環境で確認しました。

```text
PYTHONPATH=src pytest -q
11 passed in 2.35s
```

実験スクリプトも実行し、上記 JSON artifact の生成を確認済みです。`pyproject.toml` 側で未設定なら、`pytest`, `hypothesis` の dev dependency と `pythonpath = ["src"]` 相当の設定だけ追加してください。
