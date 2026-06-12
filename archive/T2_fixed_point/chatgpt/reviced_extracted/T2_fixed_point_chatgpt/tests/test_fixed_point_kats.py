from __future__ import annotations

import ast
import inspect

import pytest

import gl.fixed_point as fixed_point_module
import gl.fixed_point_alt as fixed_point_alt_module
from gl.fixed_point import fixed_point, substitute
from gl.formula import Box, Iff, Imp, Not, atom, atoms, bot
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


def assert_fixed_point(A, p, expected_H):
    H = fixed_point(A, p)

    assert p not in atoms(H)

    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", (
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
    )

    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", (
        f"GL ⊬ H ↔ A[p:=H]: H={H}"
    )


def test_engine_modules_do_not_import_provers():
    for module in (fixed_point_module, fixed_point_alt_module):
        tree = ast.parse(inspect.getsource(module))
        imported_modules = set()
        imported_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
                imported_names.update(alias.asname or alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)
                imported_names.update(alias.asname or alias.name for alias in node.names)

        assert "gl.tableau" not in imported_modules
        assert "gl.kripke_search" not in imported_modules
        assert "prove_gl" not in imported_names


def test_modalized_rejects_free_p():
    assert not is_modalized_in(atom("p"), "p")
    assert not is_modalized_in(Imp(atom("p"), Box(atom("p"))), "p")
    assert is_modalized_in(Imp(atom("q"), Box(atom("p"))), "p")

    with pytest.raises(ValueError):
        fixed_point(atom("p"), "p")


def test_henkin_without_simplifier_returns_box_top_and_prover_equiv(monkeypatch):
    """Boundary check requested in T2 revision.

    With the engine simplifier monkeypatched to identity, the Henkin input
    A(p)=□p returns □⊤ rather than syntactic ⊤.  The independent prover should
    still certify GL ⊢ □⊤ ↔ ⊤.  The production simplifier keeps exactly the
    normalization □⊤ -> ⊤ so that the known-answer test has the expected shape.
    """
    monkeypatch.setattr(fixed_point_module, "_simplify", lambda f: f)

    H = fixed_point_module.fixed_point(Box(atom("p")), "p")

    assert H == Box(Not(bot()))
    assert prove_gl(Iff(H, Not(bot()))).status == "proved"


def test_godel_fixed_point():
    """KAT 1.

    For H = ¬□⊥, the fixed-point equation is H ↔ ¬□H.

    The intended GL verification reduces to □⊥ ↔ □¬□⊥:
    - left-to-right: from □⊥ by normal modal monotonicity;
    - right-to-left: ¬□⊥ is □⊥→⊥, so □¬□⊥ is □(□⊥→⊥);
      Löb with A:=⊥ yields □(□⊥→⊥)→□⊥.
    The test itself does not encode this derivation; it asks the independent
    tableau prover to certify the biconditional.
    """
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))


def test_henkin_fixed_point():
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))


def test_lob_sentence_fixed_point():
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))


def test_box_not_fixed_point():
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))
