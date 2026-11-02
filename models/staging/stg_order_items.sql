-- Staging: order items
-- Derives line_revenue, gross_margin, margin_pct per line.
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_order_items') }}
)
SELECT
    item_id,
    order_id,
    product_id,
    TRIM(product_name)                          AS product_name,
    TRIM(category)                              AS category,
    quantity,
    unit_price,
    cost_price,
    quantity * unit_price                       AS line_revenue,
    quantity * (unit_price - cost_price)        AS gross_margin,
    ROUND(
        (unit_price - cost_price) / NULLIF(unit_price, 0) * 100, 2
    )                                           AS margin_pct
FROM source
WHERE item_id IS NOT NULL
