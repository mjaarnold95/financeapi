import uuid
from dataclasses import dataclass
from typing import Iterable

from app.models.category_rule import CategoryRule
from app.services.normalization import normalize_text

@dataclass(frozen=True)
class RuleMatchResult:
    matched: bool
    category_id: uuid.UUID | None = None
    rule_id: uuid.UUID | None = None

def _contains(haystack: str, needle: str) -> bool:
    return needle in haystack

def match_category_rule(
    rules: Iterable[CategoryRule],
    *,
    merchant_name: str | None,
    description: str,
    amount_minor: int,
) -> RuleMatchResult:
    """Return first matching rule by ascending priority."""
    m_norm = normalize_text(merchant_name or "")
    d_norm = normalize_text(description)

    sorted_rules = sorted(
        (r for r in rules if r.is_active),
        key=lambda r: (r.priority, str(r.id)),
    )

    for r in sorted_rules:
        if r.merchant_contains:
            if not _contains(m_norm, normalize_text(r.merchant_contains)):
                continue
        if r.description_contains:
            if not _contains(d_norm, normalize_text(r.description_contains)):
                continue
        if r.min_amount_minor is not None and amount_minor < r.min_amount_minor:
            continue
        if r.max_amount_minor is not None and amount_minor > r.max_amount_minor:
            continue
        return RuleMatchResult(True, category_id=r.category_id, rule_id=r.id)

    return RuleMatchResult(False, None, None)
