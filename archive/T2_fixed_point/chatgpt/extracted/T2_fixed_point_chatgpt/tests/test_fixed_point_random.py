from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from gl.fixed_point import fixed_point, substitute
from gl.formula import And, Box, Iff, Imp, Not, Or, atom, atoms, bot, modal_depth
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


TOP = Not(bot())
P_NAME = "p"
EXTRA_ATOMS = ("q", "r")


@st.composite
def modalized_formula_strategy(
    draw,
    *,
    size: int = 5,
    boxes_left: int = 3,
    under_box: bool = False,
):
    """Generate formulas modalized in p without filtering.

    The generator tracks whether the current position is already under a Box.
    atom("p") is only offered when under_box=True.
    """
    base_atoms = [atom(name) for name in EXTRA_ATOMS]
    if under_box:
        base_atoms.append(atom(P_NAME))

    base = st.one_of(
        st.sampled_from([bot(), TOP]),
        st.sampled_from(base_atoms),
    )

    if size <= 0:
        return draw(base)

    constructors = ["base", "not", "and", "or", "imp", "iff"]
    if boxes_left > 0:
        constructors.append("box")

    choice = draw(st.sampled_from(constructors))

    if choice == "base":
        return draw(base)

    if choice == "not":
        inner = draw(
            modalized_formula_strategy(
                size=size - 1,
                boxes_left=boxes_left,
                under_box=under_box,
            )
        )
        return Not(inner)

    if choice == "box":
        inner = draw(
            modalized_formula_strategy(
                size=size - 1,
                boxes_left=boxes_left - 1,
                under_box=True,
            )
        )
        return Box(inner)

    left_size = max(size - 1, 0)
    right_size = max(size - 2, 0)

    left = draw(
        modalized_formula_strategy(
            size=left_size,
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )
    right = draw(
        modalized_formula_strategy(
            size=right_size,
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )

    if choice == "and":
        return And(left, right)
    if choice == "or":
        return Or(left, right)
    if choice == "imp":
        return Imp(left, right)
    if choice == "iff":
        return Iff(left, right)

    raise AssertionError(f"unknown strategy choice: {choice!r}")


@given(A=modalized_formula_strategy())
@settings(max_examples=225, deadline=None)
def test_random_modalized_fixed_points_are_proved_by_independent_tableau(A):
    assert is_modalized_in(A, P_NAME)
    assert modal_depth(A) <= 3

    H = fixed_point(A, P_NAME)

    assert P_NAME not in atoms(H)

    fp_equation = Iff(H, substitute(A, P_NAME, H))
    result = prove_gl(fp_equation)

    assert result.status == "proved", (
        "independent prover did not certify fixed-point equation; "
        f"A={A!r}; H={H!r}; result={result!r}"
    )
