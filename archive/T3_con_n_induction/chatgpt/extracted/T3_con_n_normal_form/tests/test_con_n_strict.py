# tests/test_con_n_strict.py
import importlib
import json
from pathlib import Path

import pytest
import gl.formula as gf

bot = gf.bot
box = gf.box
neg = gf.neg


def imp(A, B):
    """A → B, with small compatibility fallbacks for formula-builder names."""
    for name in ("imp", "implies", "arrow"):
        if hasattr(gf, name):
            return getattr(gf, name)(A, B)
    for name in ("or_", "disj", "vee"):
        if hasattr(gf, name):
            return getattr(gf, name)(neg(A), B)
    raise AttributeError("gl.formula must provide imp/implies/arrow or or_/disj/vee")


def Con(n):
    """Con_n の定義通り（再帰）"""
    if n == 0:
        return neg(box(bot()))
    return neg(box(neg(Con(n - 1))))


def expected_linear_transitive_rel(num_worlds):
    """w_i R w_j iff i < j, i.e. transitive closure included."""
    return [[f"w{i}", f"w{j}"] for i in range(num_worlds) for j in range(i + 1, num_worlds)]


def load_verify_countermodel():
    """Locate T1's verify_countermodel without hard-coding a module if it moved."""
    candidates = (
        "gl.countermodel",
        "gl.model",
        "gl.models",
        "gl.semantics",
        "gl.tableau",
    )
    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        if hasattr(module, "verify_countermodel"):
            return getattr(module, "verify_countermodel")
    raise ImportError("T1 verify_countermodel が gl.* 内で見つからない")


def call_verify_countermodel(verify_countermodel, formula, model, model_path):
    """Try the common T1 call conventions while still requiring a real verification result."""
    attempts = (
        lambda: verify_countermodel(formula, model),
        lambda: verify_countermodel(model, formula),
        lambda: verify_countermodel(formula=formula, model=model),
        lambda: verify_countermodel(model=model, formula=formula),
        lambda: verify_countermodel(formula, model, root=model["root"]),
        lambda: verify_countermodel(model, formula, root=model["root"]),
        lambda: verify_countermodel(formula, str(model_path)),
        lambda: verify_countermodel(str(model_path), formula),
    )
    type_errors = []
    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            type_errors.append(str(exc))
    raise TypeError("verify_countermodel の呼び出しに失敗: " + " | ".join(type_errors))


def verification_succeeded(result):
    """Accept common success shapes: bool, dict, or result object."""
    if result is True:
        return True
    if result is False or result is None:
        return False

    if isinstance(result, dict):
        status = result.get("status")
        if isinstance(status, str):
            return status.lower() in {
                "verified",
                "valid",
                "ok",
                "countermodel",
                "counterexample",
                "falsified",
                "refuted",
            }
        for key in ("ok", "valid", "verified", "is_countermodel", "countermodel"):
            if key in result:
                return bool(result[key])
        return False

    status = getattr(result, "status", None)
    if isinstance(status, str):
        return status.lower() in {
            "verified",
            "valid",
            "ok",
            "countermodel",
            "counterexample",
            "falsified",
            "refuted",
        }
    for attr in ("ok", "valid", "verified", "is_countermodel", "countermodel"):
        if hasattr(result, attr):
            return bool(getattr(result, attr))
    return False


COUNTERMODEL_DIR = Path(__file__).resolve().parents[1] / "experiments" / "wp3" / "countermodels"


@pytest.mark.parametrize("n", range(5))
def test_strict_countermodel_shape(n):
    """strict_n{n}.json is the minimal linear (n+2)-world transitive chain."""
    model_path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))

    num_worlds = n + 2
    assert model["root"] == "w0"
    assert model["worlds"] == [f"w{i}" for i in range(num_worlds)]
    assert model["rel"] == expected_linear_transitive_rel(num_worlds)
    assert model.get("valuation", {}) == {}


@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_countermodel(n):
    """Con_n → Con_{n+1} is falsified by the minimal linear (n+2)-world GL model."""
    model_path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    formula = imp(Con(n), Con(n + 1))

    verify_countermodel = load_verify_countermodel()
    result = call_verify_countermodel(verify_countermodel, formula, model, model_path)
    assert verification_succeeded(result), \
        f"strict_n{n}.json が Con_{n} → Con_{{{n+1}}} の反例として検証されない: {result}"
