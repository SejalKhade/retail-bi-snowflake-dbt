-- Custom dbt test: completed orders must have positive net_revenue
SELECT order_id, net_revenue
FROM {{ ref('fct_orders') }}
WHERE is_completed = TRUE
  AND net_revenue <= 0
