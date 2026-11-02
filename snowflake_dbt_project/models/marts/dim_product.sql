-- Mart: dim_product (SCD Type 1 -- current snapshot)
{{ config(materialized='table') }}

SELECT
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    cost_price,
    list_price,
    standard_margin_pct
FROM {{ ref('stg_products') }}
