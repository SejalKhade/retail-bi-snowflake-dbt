-- Custom dbt test: every order item must have a matching order
SELECT i.item_id, i.order_id
FROM {{ ref('fct_order_items') }} i
LEFT JOIN {{ ref('fct_orders') }} o USING (order_id)
WHERE o.order_id IS NULL
