from src.graph import run_agent
def test_policy_cites():
    out=run_agent("What is model risk?"); assert out["route"]=="answer" and out["citations"]
def test_numeric_uses_tool():
    out=run_agent("compute VaR", {"returns":[-.1,.01,.02],"confidence":.95,"horizon_days":1}); assert "compute_var" in out["trace"]["tools"]

