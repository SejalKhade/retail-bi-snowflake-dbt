-- Semantic model: LTV and repeat-purchase rate by customer segment
{{ config(materialized='table') }}

WITH orders AS (
    SELECT * FROM {{ ref('fct_orders') }}
    WHERE is_completed = TRUE
),
segment_stats AS (
    SELECT
        customer_segment,
        COUNT(DISTINCT customer_id)                         AS unique_customers,
        COUNT(*)                                            AS total_orders,
        ROUND(SUM(net_revenue), 2)                          AS total_revenue,
        ROUND(AVG(net_revenue), 2)                          AS avg_order_value,
        ROUND(
            COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT customer_id), 0), 2
        )                                                   AS orders_per_customer,
        ROUND(
            SUM(net_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0), 2
        )                                                   AS ltv_proxy
    FROM orders
    GROUP BY customer_segment
)
SELECT * FROM segment_stats
ORDER BY ltv_proxy DESC
