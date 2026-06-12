from hypothesis import HealthCheck, given, settings, strategies as st

from gl.formula import And, Box, Iff, Imp, Not, Or, bot, modal_depth
from gl.letterless import is_letterless, letterless_normal_form
from gl.tableau import prove_gl


@st.composite
def letterless_formulas(draw, max_modal_depth=4, max_size=10):
    """Generate letterless formulas with bounded modal depth and modest size."""

    if max_size <= 1:
        return bot()

    choices = ["bot", "not"]
    if max_modal_depth > 0:
        choices.append("box")
    if max_size >= 3:
        choices.extend(["and", "or", "imp", "iff"])

    choice = draw(st.sampled_from(choices))
    if choice == "bot":
        return bot()
    if choice == "not":
        return Not(draw(letterless_formulas(max_modal_depth=max_modal_depth, max_size=max_size - 1)))
    if choice == "box":
        return Box(draw(letterless_formulas(max_modal_depth=max_modal_depth - 1, max_size=max_size - 1)))

    left_size = draw(st.integers(min_value=1, max_value=max_size - 2))
    right_size = max_size - 1 - left_size
    left = draw(letterless_formulas(max_modal_depth=max_modal_depth, max_size=left_size))
    right = draw(letterless_formulas(max_modal_depth=max_modal_depth, max_size=right_size))

    if choice == "and":
        return And(left, right)
    if choice == "or":
        return Or(left, right)
    if choice == "imp":
        return Imp(left, right)
    if choice == "iff":
        return Iff(left, right)
    raise AssertionError(f"unhandled constructor choice: {choice}")


@settings(
    max_examples=500,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
@given(letterless_formulas())
def test_random_letterless_normal_form_is_gl_equivalent(f):
    assert is_letterless(f)
    assert modal_depth(f) <= 4

    nf = letterless_normal_form(f)
    assert is_letterless(nf)
    assert prove_gl(Iff(f, nf)).status == "proved"
