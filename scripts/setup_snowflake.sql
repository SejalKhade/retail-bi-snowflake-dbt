-- =============================================================
-- Retail BI -- Snowflake Setup Script
-- Run once as ACCOUNTADMIN to create the environment
-- =============================================================

-- 1. Warehouse
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- 2. Database + schemas
CREATE DATABASE IF NOT EXISTS RETAIL_BI;
USE DATABASE RETAIL_BI;

CREATE SCHEMA IF NOT EXISTS RAW;        -- raw ingested data
CREATE SCHEMA IF NOT EXISTS STAGING;    -- dbt staging views
CREATE SCHEMA IF NOT EXISTS MARTS;      -- dbt mart tables
CREATE SCHEMA IF NOT EXISTS METRICS;    -- dbt metric aggregations

-- 3. Role + user
CREATE ROLE IF NOT EXISTS TRANSFORMER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE TRANSFORMER;
GRANT ALL ON DATABASE RETAIL_BI TO ROLE TRANSFORMER;
GRANT ALL ON ALL SCHEMAS IN DATABASE RETAIL_BI TO ROLE TRANSFORMER;
GRANT ALL ON FUTURE SCHEMAS IN DATABASE RETAIL_BI TO ROLE TRANSFORMER;
GRANT ALL ON ALL TABLES IN DATABASE RETAIL_BI TO ROLE TRANSFORMER;
GRANT ALL ON FUTURE TABLES IN DATABASE RETAIL_BI TO ROLE TRANSFORMER;

-- Assign to your user (replace YOUR_USERNAME)
-- GRANT ROLE TRANSFORMER TO USER YOUR_USERNAME;

-- 4. Raw tables (simulated Shopify / POS retail data)
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS raw_orders (
    order_id        VARCHAR(36)     NOT NULL,
    customer_id     VARCHAR(36),
    order_date      DATE            NOT NULL,
    status          VARCHAR(20),        -- completed, cancelled, returned
    channel         VARCHAR(20),        -- online, in-store, mobile
    region          VARCHAR(30),
    store_id        VARCHAR(10),
    gross_revenue   NUMERIC(10,2),
    discount_amount NUMERIC(10,2),
    shipping_cost   NUMERIC(8,2),
    item_count      INTEGER
);

CREATE TABLE IF NOT EXISTS raw_order_items (
    item_id         VARCHAR(36)     NOT NULL,
    order_id        VARCHAR(36)     NOT NULL,
    product_id      VARCHAR(36),
    product_name    VARCHAR(100),
    category        VARCHAR(50),
    quantity        INTEGER,
    unit_price      NUMERIC(10,2),
    cost_price      NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id     VARCHAR(36)     NOT NULL,
    signup_date     DATE,
    segment         VARCHAR(20),        -- new, returning, vip
    city            VARCHAR(50),
    state           VARCHAR(30),
    country         VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS raw_products (
    product_id      VARCHAR(36)     NOT NULL,
    product_name    VARCHAR(100),
    category        VARCHAR(50),
    subcategory     VARCHAR(50),
    brand           VARCHAR(50),
    cost_price      NUMERIC(10,2),
    list_price      NUMERIC(10,2)
);
