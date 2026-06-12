import pytest
from gl.formula import atom, bot, Not, Box, Imp, Iff
from gl.fixed_point import fixed_point, substitute
from gl.tableau import prove_gl

def assert_fixed_point(A, p, expected_H):
    """
    独立 prover を用いて、
    1. 生成された H が expected_H と GL 同値であること
    2. GL ⊢ H ↔ A[p:=H] が成立すること
    を検証する。
    """
    H = fixed_point(A, p)
    
    # 1. 期待される式との同値性チェック
    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", \
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
        
    # 2. 固定点方程式のチェック
    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", \
        f"GL ⊬ H ↔ A[p:=H]: H={H}"

def test_godel_fixed_point():
    """
    KAT 1: A(p) = ¬□p -> H = ¬□⊥ (Gödel sentence)
    H ↔ ¬□H は □⊥ ↔ □¬□⊥ に帰着。
    (→): □単調性。
    (←): ¬□⊥ ≡ (□⊥→⊥), ∴ □¬□⊥ ≡ □(□⊥→⊥), Löb により □⊥.
    """
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))

def test_henkin_fixed_point():
    """KAT 2: A(p) = □p -> H = ⊤"""
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))

def test_lob_fixed_point():
    """KAT 3: A(p) = □p → q -> H = □q → q"""
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))

def test_lob_instance_fixed_point():
    """KAT 4: A(p) = □¬p -> H = □⊥"""
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))