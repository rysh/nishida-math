from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from gl.fixed_point import fixed_point
from gl.fixed_point_alt import fixed_point_alt
from gl.formula import And, Box, Iff, Imp, Not, Or, atom, atoms, bot, modal_depth
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


TOP = Not(bot())
P_NAME = "p"
EXTRA_ATOMS = ("q", "r")


def assert_algorithms_agree_up_to_gl(A):
    H1 = fixed_point(A, P_NAME)
    H2 = fixed_point_alt(A, P_NAME)

    assert P_NAME not in atoms(H1)
    assert P_NAME not in atoms(H2)

    result = prove_gl(Iff(H1, H2))
    assert result.status == "proved", (
        "main and alternative fixed-point engines disagree up to GL; "
        f"A={A!r}; H1={H1!r}; H2={H2!r}; result={result!r}"
    )


def test_known_answer_outputs_agree_up_to_gl():
    cases = [
        Not(Box(atom("p"))),
        Box(atom("p")),
        Imp(Box(atom("p")), atom("q")),
        Box(Not(atom("p"))),
    ]
    for A in cases:
        assert_algorithms_agree_up_to_gl(A)


@st.composite
def modalized_formula_strategy(
    draw,
    *,
    size: int = 5,
    boxes_left: int = 3,
    under_box: bool = False,
):
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
        return Not(
            draw(
                modalized_formula_strategy(
                    size=size - 1,
                    boxes_left=boxes_left,
                    under_box=under_box,
                )
            )
        )

    if choice == "box":
        return Box(
            draw(
                modalized_formula_strategy(
                    size=size - 1,
                    boxes_left=boxes_left - 1,
                    under_box=True,
                )
            )
        )

    left = draw(
        modalized_formula_strategy(
            size=max(size - 1, 0),
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )
    right = draw(
        modalized_formula_strategy(
            size=max(size - 2, 0),
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
def test_random_main_and_alt_outputs_are_gl_equivalent(A):
    assert is_modalized_in(A, P_NAME)
    assert modal_depth(A) <= 3
    assert_algorithms_agree_up_to_gl(A)
