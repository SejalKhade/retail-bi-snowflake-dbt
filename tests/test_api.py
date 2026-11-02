"""
Retail BI API tests -- run against a mock Snowflake connection.
Uses monkeypatching so tests run in CI without real Snowflake credentials.
"""
import sys, os, types, pytest

# Stub out snowflake.connector so tests run without the real package installed
_sf = types.ModuleType("snowflake")
_sf_conn = types.ModuleType("snowflake.connector")
_sf_conn.connect = lambda **kw: None
sys.modules.setdefault("snowflake", _sf)
sys.modules.setdefault("snowflake.connector", _sf_conn)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Mock data ─────────────────────────────────────────────────────────────────
MOCK_SUMMARY = [{
    "total_orders": 3200, "total_revenue": 481000.0,
    "avg_order_value": 150.3, "avg_cancel_rate": 18.5
}]
MOCK_REVENUE = [
    {"order_month": "2024-01-01", "channel": "online",   "net_revenue": 42000.0,
     "revenue_3mo_avg": 40000.0, "cancel_rate_pct": 12.0, "avg_order_value": 155.0},
    {"order_month": "2024-01-01", "channel": "in-store", "net_revenue": 31000.0,
     "revenue_3mo_avg": 30000.0, "cancel_rate_pct": 8.0,  "avg_order_value": 140.0},
]
MOCK_CATEGORIES = [
    {"order_quarter": "2024-01-01", "category": "Electronics", "gross_revenue": 95000.0,
     "total_margin": 38000.0, "avg_margin_pct": 40.0, "revenue_rank": 1},
    {"order_quarter": "2024-01-01", "category": "Apparel", "gross_revenue": 72000.0,
     "total_margin": 32000.0, "avg_margin_pct": 44.0, "revenue_rank": 2},
]
MOCK_SEGMENTS = [
    {"customer_segment": "vip",       "unique_customers": 80,  "total_orders": 640,
     "total_revenue": 192000.0, "avg_order_value": 300.0, "orders_per_customer": 8.0,
     "ltv_proxy": 2400.0},
    {"customer_segment": "returning", "unique_customers": 200, "total_orders": 800,
     "total_revenue": 160000.0, "avg_order_value": 200.0, "orders_per_customer": 4.0,
     "ltv_proxy": 800.0},
    {"customer_segment": "new",       "unique_customers": 220, "total_orders": 440,
     "total_revenue": 88000.0,  "avg_order_value": 200.0, "orders_per_customer": 2.0,
     "ltv_proxy": 400.0},
]

import app as flask_app

@pytest.fixture(autouse=True)
def mock_query(monkeypatch):
    """Route query() to mock data based on keyword in the SQL."""
    def _mock(sql: str):
        sql_lower = sql.lower()
        if "mrt_revenue_by_channel" in sql_lower and "sum(" in sql_lower:
            return MOCK_SUMMARY
        if "mrt_revenue_by_channel" in sql_lower:
            return MOCK_REVENUE
        if "mrt_category_performance" in sql_lower:
            return MOCK_CATEGORIES
        if "mrt_customer_segments" in sql_lower:
            return MOCK_SEGMENTS
        return []
    monkeypatch.setattr(flask_app, "query", _mock)

@pytest.fixture(scope="module")
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c

# ── Tests ─────────────────────────────────────────────────────────────────────

def test_index_200(client):
    assert client.get("/").status_code == 200

def test_summary_200(client):
    assert client.get("/api/summary").status_code == 200

def test_summary_keys(client):
    d = client.get("/api/summary").get_json()
    for k in ("total_orders","total_revenue","avg_order_value","avg_cancel_rate"):
        assert k in d

def test_summary_revenue_positive(client):
    assert client.get("/api/summary").get_json()["total_revenue"] > 0

def test_revenue_by_channel_200(client):
    assert client.get("/api/revenue_by_channel").status_code == 200

def test_revenue_by_channel_is_list(client):
    data = client.get("/api/revenue_by_channel").get_json()
    assert isinstance(data, list) and len(data) > 0

def test_revenue_by_channel_fields(client):
    row = client.get("/api/revenue_by_channel").get_json()[0]
    for f in ("order_month","channel","net_revenue","cancel_rate_pct"):
        assert f in row

def test_cancel_rate_valid_range(client):
    for row in client.get("/api/revenue_by_channel").get_json():
        assert 0 <= row["cancel_rate_pct"] <= 100

def test_category_performance_200(client):
    assert client.get("/api/category_performance").status_code == 200

def test_category_performance_fields(client):
    row = client.get("/api/category_performance").get_json()[0]
    for f in ("category","gross_revenue","avg_margin_pct","revenue_rank"):
        assert f in row

def test_category_margin_valid_range(client):
    for row in client.get("/api/category_performance").get_json():
        assert 0 <= row["avg_margin_pct"] <= 100

def test_customer_segments_200(client):
    assert client.get("/api/customer_segments").status_code == 200

def test_customer_segments_fields(client):
    row = client.get("/api/customer_segments").get_json()[0]
    for f in ("customer_segment","ltv_proxy","avg_order_value","orders_per_customer"):
        assert f in row

def test_customer_segments_ltv_descending(client):
    data = client.get("/api/customer_segments").get_json()
    ltvs = [r["ltv_proxy"] for r in data]
    assert ltvs == sorted(ltvs, reverse=True), "LTV not sorted descending"

def test_customer_segments_ltv_positive(client):
    for row in client.get("/api/customer_segments").get_json():
        assert row["ltv_proxy"] > 0
