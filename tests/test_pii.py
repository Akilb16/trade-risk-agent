from src.guardrails import scan_pii
def test_planted_pii():
    found=scan_pii("email a@example.com PAN ABCDE1234F Aadhaar 1234 5678 9012")
    assert {"email","pan","aadhaar"}.issubset(found)

