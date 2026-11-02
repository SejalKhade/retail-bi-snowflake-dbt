-- Staging: customers
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_customers') }}
)
SELECT
    customer_id,
    CAST(signup_date AS DATE)   AS signup_date,
    LOWER(TRIM(segment))        AS segment,
    TRIM(city)                  AS city,
    UPPER(TRIM(state))          AS state,
    UPPER(TRIM(country))        AS country
FROM source
WHERE customer_id IS NOT NULL
