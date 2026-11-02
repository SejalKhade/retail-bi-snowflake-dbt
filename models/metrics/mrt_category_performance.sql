-- Semantic model: margin and revenue by product category x quarter
-- Uses query tuning patterns: aggregate at mart layer, not in the API.
{{ config(materialized='table') }}

WITH quarterly AS (
    SELECT
        order_quarter,
        order_year,
        category,
        subcategory,
        COUNT(DISTINCT order_id)                            AS orders_with_category,
        SUM(quantity)                                       AS units_sold,
        ROUND(SUM(line_revenue), 2)                         AS gross_revenue,
        ROUND(SUM(gross_margin), 2)                         AS total_margin,
        ROUND(AVG(margin_pct), 2)                           AS avg_margin_pct,
        RANK() OVER (
            PARTITION BY order_quarter
            ORDER BY SUM(line_revenue) DESC
        )                                                   AS revenue_rank,
        RANK() OVER (
            PARTITION BY order_quarter
            ORDER BY AVG(margin_pct) DESC
        )                                                   AS margin_rank
    FROM {{ ref('fct_order_items') }}
    WHERE is_completed = TRUE
    GROUP BY 1, 2, 3, 4
)
SELECT * FROM quarterly
ORDER BY order_quarter, revenue_rank
