# tests/test_con_n_strict.py
import json
import pytest
from pathlib import Path
from gl.formula import bot, box, neg, implies
from gl.tableau import prove_gl, verify_countermodel
from test_con_n_normal_form import box_n, Con

@pytest.mark.parametrize("n", range(5))
def test_con_n_strict(n):
    """Con_n → Con_{n+1} は証明不可であり、反例モデルで棄却される"""
    formula = implies(Con(n), Con(n + 1))
    result = prove_gl(formula)
    
    # 1. 証明不可であることを確認
    assert result.status == "unproved", \
        f"Con_{n} → Con_{n+1} が誤って証明された: {result}"
    
    # 2. 事前生成した反例モデルの読み込みと検証
    model_path = Path(f"experiments/wp3/countermodels/strict_n{n}.json")
    with open(model_path, "r") as f:
        model = json.load(f)
    
    # モデルのroot (w0) において、式が False になることを検証
    is_valid_in_model = verify_countermodel(formula, model, root="w0")
    assert is_valid_in_model is False, \
        f"反例モデル strict_n{n}.json で式が反証されなかった"

def generate_strict_countermodels():
    """反例モデル (n+2)-chain を生成するスクリプト"""
    out_dir = Path("experiments/wp3/countermodels")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for n in range(5):
        # n+2 個の世界を持つ線形鎖（推移閉包込み）
        num_worlds = n + 2
        worlds = [f"w{i}" for i in range(num_worlds)]
        
        # GL は推移的であるため、推移閉包を明示的に構築する
        relations = {
            f"w{i}": [f"w{j}" for j in range(i + 1, num_worlds)]
            for i in range(num_worlds)
        }
        
        model = {
            "worlds": worlds,
            "relations": relations,
            "valuation": {}  # bot は常に false なので空でよい
        }
        
        with open(out_dir / f"strict_n{n}.json", "w") as f:
            json.dump(model, f, indent=2)

if __name__ == "__main__":
    generate_strict_countermodels()