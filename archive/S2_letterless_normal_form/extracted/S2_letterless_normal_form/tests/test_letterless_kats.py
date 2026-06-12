import pytest

from gl.formula import And, Box, Iff, Imp, Not, Or, atom, bot, box_power
from gl.letterless import is_letterless, letterless_normal_form, nf_equiv
from gl.tableau import prove_gl


def check(input_f, expected_nf):
    nf = letterless_normal_form(input_f)
    assert prove_gl(Iff(input_f, nf)).status == "proved", (
        f"input not GL-equivalent to its NF: {input_f} vs {nf}"
    )
    assert prove_gl(Iff(nf, expected_nf)).status == "proved", (
        f"NF not GL-equivalent to expected: {nf} vs {expected_nf}"
    )


def test_bot_reduces_to_box0_bot():
    check(bot(), box_power(bot(), 0))


def test_top_reduces_to_not_box0_bot():
    check(Not(bot()), Not(box_power(bot(), 0)))


def test_box_bot_reduces_to_box1_bot():
    check(Box(bot()), box_power(bot(), 1))


def test_box_box_bot_reduces_to_box2_bot():
    check(Box(Box(bot())), box_power(bot(), 2))


def test_not_box_bot_reduces_to_not_box1_bot():
    check(Not(Box(bot())), Not(box_power(bot(), 1)))


def test_not_box_not_box_bot_reduces_to_not_box1_bot():
    # Note: Box(Not(Box(bot()))) is the same formula as the Loeb-instance KAT
    # Box(Imp(Box(bot()), bot())) up to propositional equivalence, hence its
    # negation is GL-equivalent to Not(box_power(bot(), 1)), not Not(box_power(bot(), 2)).
    check(Not(Box(Not(Box(bot())))), Not(box_power(bot(), 1)))


def test_not_box_box_bot_reduces_to_not_box2_bot():
    check(Not(Box(Box(bot()))), Not(box_power(bot(), 2)))


def test_excluded_middle_reduces_to_top():
    check(Or(Box(bot()), Not(Box(bot()))), Not(bot()))


def test_contradiction_reduces_to_bot():
    check(And(Box(bot()), Not(Box(bot()))), bot())


def test_loeb_instance_absorbs_to_box1_bot():
    check(Box(Imp(Box(bot()), bot())), box_power(bot(), 1))


def test_box_top_reduces_to_top():
    check(Box(Not(bot())), Not(bot()))


def test_nf_equiv_is_not_syntactic_identity():
    assert nf_equiv(Box(Not(bot())), Not(bot()))


def test_non_letterless_is_rejected():
    assert not is_letterless(atom("p"))
    with pytest.raises(ValueError):
        letterless_normal_form(atom("p"))
    with pytest.raises(ValueError):
        nf_equiv(atom("p"), bot())
