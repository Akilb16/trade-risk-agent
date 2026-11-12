def judge(answer: str, reference: str, expected_source: str) -> dict:
    grounded = 5 if expected_source != "none" and "[cite:" in answer else 1
    correct = 5 if reference.lower().split()[0] in answer.lower() else 2
    citation = 5 if "[cite:" in answer else 1
    return {"groundedness":grounded,"correctness":correct,"citation_accuracy":citation,"reason":"deterministic baseline judge"}

