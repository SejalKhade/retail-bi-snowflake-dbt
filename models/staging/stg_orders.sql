-- Staging: orders
-- Cleans status values, derives net_revenue, casts dates.
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_orders') }}
),
cleaned AS (
    SELECT
        order_id,
        customer_id,
        CAST(order_date AS DATE)                        AS order_date,
        LOWER(TRIM(status))                             AS status,
        LOWER(TRIM(channel))                            AS channel,
        TRIM(region)                                    AS region,
        store_id,
        COALESCE(gross_revenue, 0)                      AS gross_revenue,
        COALESCE(discount_amount, 0)                    AS discount_amount,
        COALESCE(shipping_cost, 0)                      AS shipping_cost,
        COALESCE(item_count, 0)                         AS item_count,
        gross_revenue - COALESCE(discount_amount, 0)
            + COALESCE(shipping_cost, 0)                AS net_revenue,
        status = 'completed'                            AS is_completed,
        status IN ('cancelled','returned')              AS is_cancelled
    FROM source
    WHERE order_id IS NOT NULL
)
SELECT * FROM cleaned
