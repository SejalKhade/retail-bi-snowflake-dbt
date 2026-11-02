-- Mart: fct_order_items
-- Line-level fact with product and order context joined in.
{{
  config(
    materialized='table',
    cluster_by=['order_id']
  )
}}

WITH items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),
orders AS (
    SELECT order_id, order_date, order_month, order_quarter, order_year,
           channel, region, status, is_completed, customer_segment
    FROM {{ ref('fct_orders') }}
),
products AS (
    SELECT * FROM {{ ref('stg_products') }}
)
SELECT
    i.item_id,
    i.order_id,
    i.product_id,
    o.order_date,
    o.order_month,
    o.order_quarter,
    o.order_year,
    o.channel,
    o.region,
    o.status,
    o.is_completed,
    o.customer_segment,
    p.category,
    p.subcategory,
    p.brand,
    i.quantity,
    i.unit_price,
    i.cost_price,
    i.line_revenue,
    i.gross_margin,
    i.margin_pct
FROM items i
LEFT JOIN orders  o USING (order_id)
LEFT JOIN products p USING (product_id)
