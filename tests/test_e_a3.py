"""KAT for E-A3: Gödel seed launches, Henkin seed flatlines, same engine.

The single fixed-point engine is `gl.fixed_point.fixed_point`. The two seed
bodies differ by exactly one negation around `□p`. The Gödel seed lands on
`Con_0 = ¬□⊥` (a GL non-theorem; the first rung of the E-A2 ladder); the
Henkin seed lands on `⊤` (a GL theorem; adjoining it adds no new letterless
consequences). These tests assert all of that with the canonical
`prove_gl(Iff(...)).status == "proved"` pattern.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import experiments.wp3a.e_a3_henkin_vs_godel as e_a3
from gl.fixed_point import fixed_point
from gl.formula import Box, Iff, Imp, Not, atom, bot, con
from gl.letterless import nf_equiv
from gl.tableau import prove_gl


P = "p"
GODEL_BODY = Not(Box(atom(P)))
HENKIN_BODY = Box(atom(P))


def test_seeds_differ_only_by_negation():
    """Document that the two bodies are related by one ``Not`` insertion."""
    godel_json = GODEL_BODY.to_json()
    henkin_json = HENKIN_BODY.to_json()
    assert godel_json == {"type": "not", "arg": henkin_json}


def test_same_engine_function_for_both_seeds():
    """Both sides must call the same engine — no dispatch on the seed shape."""
    assert e_a3.fixed_point is fixed_point
    assert inspect.getsourcefile(fixed_point).endswith("fixed_point.py")


def test_godel_seed_reduces_to_con0():
    H = fixed_point(GODEL_BODY, P)
    assert prove_gl(Iff(H, con(0))).status == "proved"
    assert nf_equiv(H, con(0))


def test_henkin_seed_reduces_to_top():
    H = fixed_point(HENKIN_BODY, P)
    assert prove_gl(Iff(H, Not(bot()))).status == "proved"
    assert nf_equiv(H, Not(bot()))


def test_godel_seed_is_not_a_gl_theorem():
    """Con_0 is *not* a GL theorem — this is exactly what makes it launch."""
    H = fixed_point(GODEL_BODY, P)
    assert prove_gl(H).status == "refuted"


def test_henkin_seed_is_a_gl_theorem():
    """K = ⊤, which is a GL theorem — this is exactly what makes it flatline."""
    H = fixed_point(HENKIN_BODY, P)
    assert prove_gl(H).status == "proved"


def test_godel_does_not_imply_higher_con_n():
    """Con_0 does not entail Con_{n+1} for any n; matches the E-A2 ladder."""
    H = fixed_point(GODEL_BODY, P)
    for n in range(5):
        assert prove_gl(Imp(H, con(n + 1))).status == "refuted"


def test_henkin_flatline_for_letterless_sample():
    """For every letterless B in the sample, GL ⊢ (K → B) ↔ B."""
    H = fixed_point(HENKIN_BODY, P)
    sample = [bot(), Not(bot()), Box(bot()), con(0), con(1), con(2)]
    for B in sample:
        assert prove_gl(Iff(Imp(H, B), B)).status == "proved", (
            f"Henkin seed surprisingly changed the GL status of B={B}"
        )


def test_artifacts_are_consistent_with_summary():
    """The committed artifact should match the live engine's classifications."""
    artifact_path = (
        Path(__file__).resolve().parent.parent
        / "experiments"
        / "wp3a"
        / "artifacts"
        / "e_a3_godel_vs_henkin.json"
    )
    payload = json.loads(artifact_path.read_text())
    assert payload["godel_seed"]["gl_proves_reduction_to_con0"] is True
    assert payload["godel_seed"]["is_gl_theorem"] is False
    assert payload["godel_seed"]["letterless_nf_equiv_con0"] is True
    assert payload["henkin_seed"]["gl_proves_reduction_to_top"] is True
    assert payload["henkin_seed"]["is_gl_theorem"] is True
    assert payload["henkin_seed"]["letterless_nf_equiv_top"] is True
    assert payload["seed_delta"]["structural_check"] is True
