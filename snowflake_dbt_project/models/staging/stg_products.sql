-- Staging: products
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_products') }}
)
SELECT
    product_id,
    TRIM(product_name)      AS product_name,
    TRIM(category)          AS category,
    TRIM(subcategory)       AS subcategory,
    TRIM(brand)             AS brand,
    cost_price,
    list_price,
    ROUND((list_price - cost_price) / NULLIF(list_price,0) * 100, 2)
                            AS standard_margin_pct
FROM source
WHERE product_id IS NOT NULL
