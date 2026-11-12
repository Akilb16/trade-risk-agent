from src.tools.var import compute_var
def test_var_positive_and_horizon_scaling():
    one=compute_var([-0.1,-0.05,0.01,0.02],.75,1); two=compute_var([-0.1,-0.05,0.01,0.02],.75,4)
    assert one > 0 and abs(two/one-2)<1e-9

