import pytest

from gl.formula import And, Box, Iff, Imp, Not, Or, atom, bot, box_power
from gl.letterless import is_letterless, letterless_normal_form, nf_equiv
from gl.tableau import prove_gl


def test_letterless_does_not_import_provers():
    import ast
    import inspect

    import gl.letterless as letterless_module

    tree = ast.parse(inspect.getsource(letterless_module))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
    assert "gl.tableau" not in imported_modules
    assert "gl.kripke_search" not in imported_modules


def check(input_f, expected_nf):
    nf = letterless_normal_form(input_f)
    # 構文一致は要求しない。GL-同値かを独立 prover で確認
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
    # Corrected dispatch KAT: Not(Box(Not(Box(bot())))) is GL-equivalent to
    # Not(box_power(bot(), 1)), not Not(box_power(bot(), 2)).
    check(Not(Box(Not(Box(bot())))), Not(box_power(bot(), 1)))


def test_not_box_box_bot_reduces_to_not_box2_bot():
    # This is the nearby formula whose expected normal form is Not(box_power(bot(), 2)).
    check(Not(Box(Box(bot()))), Not(box_power(bot(), 2)))


def test_excluded_middle_reduces_to_top():
    check(Or(Box(bot()), Not(Box(bot()))), Not(bot()))


def test_contradiction_reduces_to_bot():
    check(And(Box(bot()), Not(Box(bot()))), bot())


def test_loeb_instance_absorbs_to_box1_bot():
    check(Box(Imp(Box(bot()), bot())), box_power(bot(), 1))


def test_box_top_reduces_to_top():
    check(Box(Not(bot())), Not(bot()))


def test_nf_equiv_is_gl_equivalence_not_syntactic_identity():
    assert nf_equiv(Box(Not(bot())), Not(bot()))
    assert nf_equiv(Box(Imp(Box(bot()), bot())), Box(bot()))


def test_non_letterless_is_rejected():
    assert not is_letterless(atom("p"))
    with pytest.raises(ValueError):
        letterless_normal_form(atom("p"))
    with pytest.raises(ValueError):
        nf_equiv(atom("p"), bot())
