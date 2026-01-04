import uuid
from app.services.rules_engine import match_category_rule
from app.models.category_rule import CategoryRule

def _rule(**kwargs):
    # minimal init for unit test; SQLAlchemy mapped object works as plain class too
    r = CategoryRule()
    for k, v in kwargs.items():
        setattr(r, k, v)
    if not hasattr(r, "id") or r.id is None:
        r.id = uuid.uuid4()
    return r

def test_rule_priority_and_matching():
    cat_a = uuid.uuid4()
    cat_b = uuid.uuid4()

    rules = [
        _rule(priority=200, is_active=True, description_contains="COFFEE", category_id=cat_a),
        _rule(priority=10, is_active=True, merchant_contains="STARBUCKS", category_id=cat_b),
    ]

    res = match_category_rule(rules, merchant_name="Starbucks Store 123", description="Coffee", amount_minor=-500)
    assert res.matched is True
    assert res.category_id == cat_b

def test_rule_amount_range():
    cat = uuid.uuid4()
    rules = [
        _rule(priority=1, is_active=True, description_contains="RENT", min_amount_minor=-300000, max_amount_minor=-100000, category_id=cat),
    ]
    assert match_category_rule(rules, merchant_name=None, description="Rent", amount_minor=-200000).matched is True
    assert match_category_rule(rules, merchant_name=None, description="Rent", amount_minor=-50000).matched is False
