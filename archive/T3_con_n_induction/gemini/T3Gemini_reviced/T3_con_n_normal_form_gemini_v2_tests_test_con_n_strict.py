import json
import pytest
from pathlib import Path
from gl.formula import Imp
from gl.tableau import prove_gl
from gl.countermodel_verifier import verify_countermodel
from test_con_n_normal_form import Con

@pytest.mark.parametrize("n", range(5))
def test_con_n_strict(n: int):
    formula = Imp(Con(n), Con(n + 1))
    result = prove_gl(formula)
    assert result.status == "refuted"
    assert result.countermodel is not None

@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_countermodel(n: int):
    model = json.loads(Path(f"experiments/wp3/countermodels/strict_n{n}.json").read_text())
    formula = Imp(Con(n), Con(n + 1))
    assert verify_countermodel(formula, model)
