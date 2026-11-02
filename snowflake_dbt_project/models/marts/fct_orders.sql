-- Mart: fct_orders
-- Central fact table. Joins orders to customers + derives fiscal period.
-- Materialized as TABLE for query performance; cluster on order_date.
{{
  config(
    materialized='table',
    cluster_by=['order_date']
  )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
enriched AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        DATE_TRUNC('month', o.order_date)   AS order_month,
        DATE_TRUNC('quarter', o.order_date) AS order_quarter,
        EXTRACT(year FROM o.order_date)     AS order_year,
        o.status,
        o.channel,
        o.region,
        o.store_id,
        o.gross_revenue,
        o.discount_amount,
        o.shipping_cost,
        o.net_revenue,
        o.item_count,
        o.is_completed,
        o.is_cancelled,
        c.segment                           AS customer_segment,
        c.state                             AS customer_state
    FROM orders o
    LEFT JOIN customers c USING (customer_id)
)
SELECT * FROM enriched
