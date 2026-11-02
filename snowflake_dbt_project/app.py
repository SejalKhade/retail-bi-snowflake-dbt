"""
Retail BI Dashboard -- Flask API
Reads from Snowflake METRICS schema (dbt mart tables).
All heavy aggregation is pre-computed in dbt; API just fetches and serves.
"""
import os
from flask import Flask, jsonify, render_template
import snowflake.connector
import pandas as pd

app = Flask(__name__)


def get_conn():
    return snowflake.connector.connect(
        account   = os.environ["SNOWFLAKE_ACCOUNT"],
        user      = os.environ["SNOWFLAKE_USER"],
        password  = os.environ["SNOWFLAKE_PASSWORD"],
        role      = "TRANSFORMER",
        warehouse = "COMPUTE_WH",
        database  = "RETAIL_BI",
        schema    = "METRICS",
    )


def query(sql: str) -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql)
    cols = [d[0].lower() for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    rows = query("""
        SELECT
            SUM(total_orders)       AS total_orders,
            SUM(net_revenue)        AS total_revenue,
            ROUND(AVG(avg_order_value), 2)  AS avg_order_value,
            ROUND(AVG(cancel_rate_pct), 2)  AS avg_cancel_rate
        FROM RETAIL_BI.METRICS.MRT_REVENUE_BY_CHANNEL
    """)
    return jsonify(rows[0] if rows else {})


@app.route("/api/revenue_by_channel")
def revenue_by_channel():
    rows = query("""
        SELECT order_month, channel, net_revenue,
               revenue_3mo_avg, cancel_rate_pct, avg_order_value
        FROM RETAIL_BI.METRICS.MRT_REVENUE_BY_CHANNEL
        ORDER BY order_month, channel
    """)
    # Convert Snowflake date objects to string for JSON
    for r in rows:
        if hasattr(r.get("order_month"), "isoformat"):
            r["order_month"] = r["order_month"].isoformat()
    return jsonify(rows)


@app.route("/api/category_performance")
def category_performance():
    rows = query("""
        SELECT order_quarter, category, gross_revenue,
               total_margin, avg_margin_pct, revenue_rank
        FROM RETAIL_BI.METRICS.MRT_CATEGORY_PERFORMANCE
        ORDER BY order_quarter, revenue_rank
        LIMIT 60
    """)
    for r in rows:
        if hasattr(r.get("order_quarter"), "isoformat"):
            r["order_quarter"] = r["order_quarter"].isoformat()
    return jsonify(rows)


@app.route("/api/customer_segments")
def customer_segments():
    rows = query("""
        SELECT customer_segment, unique_customers, total_orders,
               total_revenue, avg_order_value, orders_per_customer, ltv_proxy
        FROM RETAIL_BI.METRICS.MRT_CUSTOMER_SEGMENTS
        ORDER BY ltv_proxy DESC
    """)
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, port=5051)
