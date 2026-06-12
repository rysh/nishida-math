# tests/test_con_n_strict.py
import json
from pathlib import Path

import pytest
from gl.countermodel_verifier import verify_countermodel
from gl.formula import bot, Box, Not, Imp
from gl.tableau import prove_gl


def Con(n: int):
    """Con_n の定義通り（再帰）"""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))


def expected_linear_transitive_rel(num_worlds: int) -> list[list[int]]:
    """i R j iff i < j, with transitive closure included explicitly."""
    return [[i, j] for i in range(num_worlds) for j in range(i + 1, num_worlds)]


COUNTERMODEL_DIR = Path(__file__).resolve().parents[1] / "experiments" / "wp3" / "countermodels"


@pytest.mark.parametrize("n", range(5))
def test_strict_countermodel_json_shape(n: int):
    """strict_n{n}.json is the minimal linear (n+2)-world transitive GL frame."""
    model_path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    formula = Imp(Con(n), Con(n + 1))

    num_worlds = n + 2
    assert model["worlds"] == list(range(num_worlds))
    assert model["rel"] == expected_linear_transitive_rel(num_worlds)
    assert model["val"] == {}
    assert model["refutes"] == {"formula": formula.to_json(), "at": 0}
    assert model["checks"] == {"transitive": True, "irreflexive": True}


@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_countermodel(n: int):
    """Con_n → Con_{n+1} is falsified by strict_n{n}.json at world 0."""
    model_path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    formula = Imp(Con(n), Con(n + 1))
    assert verify_countermodel(formula, model), \
        f"strict_n{n}.json が Con_{n} → Con_{{{n + 1}}} の反例として検証されない"


@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_is_refuted_by_tableau(n: int):
    """GL ⊬ Con_n → Con_{n+1}; T1 tableau should report refuted."""
    formula = Imp(Con(n), Con(n + 1))
    result = prove_gl(formula)
    assert result.status == "refuted", \
        f"Con_{n} → Con_{{{n + 1}}} は GL で refuted になるべき: {result}"
