import re

_whitespace_re = re.compile(r"\s+")
_noise_re = re.compile(r"[\t\n\r]+")

def normalize_text(s: str) -> str:
    """Normalize free text for matching/dedup (deterministic, conservative)."""
    s = s or ""
    s = _noise_re.sub(" ", s)
    s = s.strip().upper()
    s = _whitespace_re.sub(" ", s)
    return s

def normalize_merchant_name(s: str) -> str:
    # Slightly more aggressive; remove some punctuation.
    s = normalize_text(s)
    s = re.sub(r"[^A-Z0-9 ]+", "", s)
    s = _whitespace_re.sub(" ", s).strip()
    return s
