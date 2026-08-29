"""Tests — run with: python -m oracle.tests.test"""
from oracle.store import upsert_opp, upsert_svc, stats, q


def test_opp():
    upsert_opp({"id": "test:1", "src": "test", "source_id": "1",
                "title": "Test Bounty", "desc": "A test", "cat": "code",
                "skills": ["python"], "reward": 50, "currency": "USD", "status": "open"})
    rows = q("SELECT * FROM opp WHERE id='test:1'")
    assert len(rows) == 1
    assert rows[0]["reward"] == 50
    print("  ✓ opp insert")


def test_svc():
    upsert_svc({"id": "test:svc1", "src": "test", "source_id": "s1",
                "name": "Test API", "desc": "A test API", "cat": "data",
                "price": 0.01, "calls": 1000, "rating": 4.5})
    rows = q("SELECT * FROM svc WHERE id='test:svc1'")
    assert len(rows) == 1
    assert rows[0]["calls"] == 1000
    print("  ✓ svc insert")


def test_stats():
    s = stats()
    assert s["opp"] >= 1
    assert s["svc"] >= 1
    print("  ✓ stats")


def test_query():
    rows = q("SELECT * FROM opp WHERE src='test'")
    assert len(rows) >= 1
    print("  ✓ query")


if __name__ == "__main__":
    print("=== Oracle Tests ===")
    test_opp()
    test_svc()
    test_stats()
    test_query()
    print("All passed!")
