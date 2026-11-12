import re
from dataclasses import dataclass

PATTERNS = {
    "email": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
    "mobile": r"(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)",
    "pan": r"\b[A-Z]{5}\d{4}[A-Z]\b",
    "aadhaar": r"(?<!\d)(?:\d{4}[ -]?){2}\d{4}(?!\d)",
    "card": r"(?<![\d.])(?:\d[ -]?){13,19}(?![\d.])",
}
@dataclass
class GuardrailResult:
    allowed: bool; text: str; reasons: list[str]

def scan_pii(text: str) -> list[str]:
    return [name for name, pattern in PATTERNS.items() if re.search(pattern, text, re.I)]

def input_guardrail(text: str) -> GuardrailResult:
    reasons=[]
    if not text.strip(): reasons.append("empty_input")
    if len(text) > 4000: reasons.append("input_too_long")
    pii=scan_pii(text)
    if pii: reasons.append("pii:" + ",".join(pii))
    if not any(k in text.lower() for k in ("risk", "var", "greek", "delta", "gamma", "vega", "theta", "rho", "stress", "limit", "regulat", "basel", "rbi", "model risk")):
        reasons.append("off_topic")
    return GuardrailResult(not reasons, text, reasons)

def output_guardrail(answer: str, citations: set[str]) -> GuardrailResult:
    reasons=[]
    cited=set(re.findall(r"\[cite:([^\]]+)\]", answer))
    if not cited or not cited.issubset(citations): reasons.append("invalid_or_missing_citation")
    pii=scan_pii(answer)
    if pii: reasons.append("pii:" + ",".join(pii))
    return GuardrailResult(not reasons, answer, reasons)

