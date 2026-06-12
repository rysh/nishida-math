import pytest
import ast
import inspect
from gl.formula import atom, bot, Not, Box, Imp, Iff
import gl.fixed_point as fixed_point_module
import gl.fixed_point_alt as fixed_point_alt_module
from gl.fixed_point import fixed_point, substitute
from gl.tableau import prove_gl

def test_engine_modules_do_not_import_provers():
    """ASTレベルでのコード隔離不変式テスト"""
    for module in (fixed_point_module, fixed_point_alt_module):
        tree = ast.parse(inspect.getsource(module))
        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)
        assert "gl.tableau" not in imported_modules
        assert "gl.kripke_search" not in imported_modules

def assert_fixed_point(A, p, expected_H):
    """独立証明器による外部検証を徹底（構文一致比較による自己満足の排除）"""
    H = fixed_point(A, p)
    
    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", \
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
        
    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", \
        f"GL ⊬ H ↔ A[p:=H]: H={H}"

def test_godel_fixed_point():
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))

def test_henkin_fixed_point():
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))

def test_lob_fixed_point():
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))

def test_lob_instance_fixed_point():
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))