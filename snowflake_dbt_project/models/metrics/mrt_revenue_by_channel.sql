-- Semantic model: revenue KPIs by channel x month
-- Exposes the "single trusted metric source" pattern interviewers ask about.
{{ config(materialized='table') }}

WITH base AS (
    SELECT
        order_month,
        order_year,
        channel,
        COUNT(*)                                            AS total_orders,
        SUM(CASE WHEN is_completed THEN 1 ELSE 0 END)      AS completed_orders,
        SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END)      AS cancelled_orders,
        ROUND(SUM(net_revenue), 2)                          AS net_revenue,
        ROUND(SUM(gross_revenue), 2)                        AS gross_revenue,
        ROUND(SUM(discount_amount), 2)                      AS total_discounts,
        ROUND(AVG(net_revenue), 2)                          AS avg_order_value,
        ROUND(
            100.0 * SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0), 1
        )                                                   AS cancel_rate_pct
    FROM {{ ref('fct_orders') }}
    GROUP BY 1, 2, 3
),
with_mom AS (
    SELECT *,
        ROUND(
            net_revenue - LAG(net_revenue) OVER (
                PARTITION BY channel ORDER BY order_month
            ), 2
        )                                                   AS revenue_mom_delta,
        ROUND(
            AVG(net_revenue) OVER (
                PARTITION BY channel
                ORDER BY order_month
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 2
        )                                                   AS revenue_3mo_avg
    FROM base
)
SELECT * FROM with_mom
ORDER BY order_month, channel
