"""
Random battery test for GL provers.
Generate 1000 random modal formulas depth<=3, atoms<=3.
Both methods must agree on status, and if refuted, countermodel must verify.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from hypothesis.strategies import composite
from src.gl.formula import (
    Formula, Atom, Not, And, Or, Imp, Iff, Box,
    modal_depth, to_json, from_json, pretty
)
from src.gl.tableau import prove_gl_tableau
from src.gl.kripke_search import prove_gl_kripke
from src.gl.countermodel_verifier import verify_countermodel


# Strategy for random formulas with controlled depth and atoms
def atom_strategy():
    return st.sampled_from(["p", "q", "r"])


@composite
def formula_strategy(draw, max_depth=3, max_atoms=3):
    depth = draw(st.integers(min_value=0, max_value=max_depth))
    atoms = draw(st.lists(atom_strategy(), min_size=1, max_size=max_atoms, unique=True))
    # recursive build
    def build(d):
        if d == 0:
            return Atom(draw(st.sampled_from(atoms)))
        # mix constructors weighted
        choice = draw(st.integers(0, 6))
        if choice == 0:
            return Not(build(d-1 if d>0 else 0))
        elif choice == 1:
            a1 = build(d-1 if d>0 else 0)
            a2 = build(d-1 if d>0 else 0)
            return And((a1, a2))
        elif choice == 2:
            a1 = build(d-1 if d>0 else 0)
            a2 = build(d-1 if d>0 else 0)
            return Or((a1, a2))
        elif choice == 3:
            return Imp(build(d-1 if d>0 else 0), build(d-1 if d>0 else 0))
        elif choice == 4:
            return Iff(build(d-1 if d>0 else 0), build(d-1 if d>0 else 0))
        elif choice == 5:
            return Box(build(d-1 if d>0 else 0))
        else:
            return Not(build(d))  # extra not
    return build(depth)


@settings(max_examples=1000, deadline=5000, phases=[Phase.generate])  # generous time
@given(f=formula_strategy())
def test_random_agreement(f):
    # Both must give same status
    res_t = prove_gl_tableau(f)
    res_k = prove_gl_kripke(f)
    assert res_t["status"] == res_k["status"], (
        f"Disagreement on {pretty(f)} (D={modal_depth(f)}): "
        f"tableau={res_t['status']} kripke={res_k['status']}"
    )
    # If refuted, both should have valid countermodel (kripke guarantees, tableau delegates)
    if res_k["status"] == "refuted":
        cm = res_k["countermodel"]
        assert cm is not None
        vres = verify_countermodel(cm)
        assert vres["valid"], f"Invalid countermodel for {pretty(f)}: {vres['reason']}"
    # No case of proved and refuted at same time (already by status assert)
