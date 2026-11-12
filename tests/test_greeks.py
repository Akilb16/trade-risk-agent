from src.tools.greeks import compute_greeks
def test_textbook_shape():
    g=compute_greeks(100,100,1,.05,.2,"call"); assert 0 < g["delta"] < 1 and g["gamma"] > 0 and g["vega"] > 0

