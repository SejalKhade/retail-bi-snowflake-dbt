-- Custom dbt test: overall cancellation rate must stay below 50%
-- Fails (returns rows) if the rate exceeds threshold.
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 2
    ) AS cancel_rate_pct
FROM {{ ref('fct_orders') }}
HAVING cancel_rate_pct > 50
