# Retail BI — Snowflake + dbt + Flask + D3.js

End-to-end BI pipeline: raw retail data → Snowflake → dbt semantic models → Flask API → D3.js dashboard.

Built to demonstrate the full BI developer stack: dimensional modeling in Snowflake, a dbt semantic layer with custom data tests, a Flask API serving pre-aggregated marts, and a D3.js frontend with four charts and KPI tiles.

---

## Architecture

```
Raw data (POS/Shopify-style)
    │
    ▼
Snowflake RAW schema
    │
    ▼ dbt staging (views)
stg_orders → stg_order_items → stg_customers → stg_products
    │
    ▼ dbt marts (tables, clustered)
fct_orders + fct_order_items + dim_product
    │
    ▼ dbt metrics (semantic models)
mrt_revenue_by_channel   — revenue + cancel rate, MoM delta, 3-month rolling avg
mrt_category_performance — margin + revenue rank by category per quarter
mrt_customer_segments    — LTV proxy, orders per customer, AOV by segment
    │
    ▼
Flask API (5 endpoints) → D3.js dashboard
```

---

## Why This Stack

| Decision | Reason |
|---|---|
| Snowflake | Cloud-native warehouse, auto-suspend on free tier = $0 dev cost |
| dbt for transformation | SQL-first, version-controlled, testable semantic layer |
| Cluster by order_date | Snowflake query tuning — eliminates full table scans on date-range queries |
| Flask API serves marts | Heavy aggregation pre-computed in dbt; API just fetches — fast, cheap queries |
| D3.js frontend | Full control over visualization; no chart library lock-in |
| GitHub Actions CI | dbt build + dbt test + pytest on every push; secrets via GitHub Secrets |

---

## Setup

### 1. Snowflake (free trial at snowflake.com)

```sql
-- Run scripts/setup_snowflake.sql as ACCOUNTADMIN
-- Creates: RETAIL_BI database, RAW/STAGING/MARTS/METRICS schemas, TRANSFORMER role, COMPUTE_WH
```

### 2. Environment variables

```bash
export SNOWFLAKE_ACCOUNT=your_account_id   # e.g. abc12345.us-east-1
export SNOWFLAKE_USER=your_username
export SNOWFLAKE_PASSWORD=your_password
```

### 3. Install + load data

```bash
pip install -r requirements.txt
python scripts/generate_and_load.py
# → loads 500 customers, 80 products, 4,000 orders, ~14,000 items into RAW schema
```

### 4. Run dbt

```bash
dbt deps
dbt build      # compile + test + run all models
dbt test       # re-run tests only
```

### 5. Start dashboard

```bash
python app.py
# → http://localhost:5051
```

---

## dbt Model Lineage

```
sources (RAW)
  └─ stg_orders
  └─ stg_order_items
  └─ stg_customers
  └─ stg_products
        │
        ▼
  fct_orders ─────────────────── fct_order_items
        │                               │
        └──────────┬────────────────────┘
                   ▼
    mrt_revenue_by_channel
    mrt_category_performance
    mrt_customer_segments
```

---

## Tests

**dbt tests (Snowflake-side):**
- Source freshness + uniqueness + not_null on all PKs
- `accepted_values` on status and channel
- 3 custom SQL tests: cancel rate < 50%, no orphan items, revenue > 0 for completed orders

**pytest tests (mocked, CI-friendly — no Snowflake creds needed):**
```bash
pytest tests/test_api.py -v --cov=app --cov-report=term-missing
# 15/15 passing, ~90% coverage
```

---

## API Endpoints

| Endpoint | Serves |
|---|---|
| `GET /` | Dashboard UI |
| `GET /api/summary` | KPI header tiles |
| `GET /api/revenue_by_channel` | Monthly revenue + cancel rate per channel with MoM delta |
| `GET /api/category_performance` | Quarterly revenue rank + margin by product category |
| `GET /api/customer_segments` | LTV proxy, AOV, orders/customer by segment |

---

## What's Next

- Connect to a live Shopify or Stripe API instead of simulated data
- Add dbt incremental models for daily loads (MERGE INTO pattern)
- Deploy Flask to Azure App Service or AWS ECS
- Add Azure Key Vault / AWS Secrets Manager for credential rotation
