"""
Retail BI -- Data Generator + Snowflake Loader
Generates realistic retail data and loads it into Snowflake RAW schema.
Run after setup_snowflake.sql.

Usage:
    export SNOWFLAKE_ACCOUNT=... SNOWFLAKE_USER=... SNOWFLAKE_PASSWORD=...
    python scripts/generate_and_load.py
"""
import os, uuid, random, math
from datetime import date, timedelta
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# ── Config ────────────────────────────────────────────────────────────────────
SEED           = 42
N_CUSTOMERS    = 500
N_PRODUCTS     = 80
N_ORDERS       = 4000
START_DATE     = date(2024, 1, 1)
END_DATE       = date(2024, 12, 31)

REGIONS        = ["Northeast", "Southeast", "Midwest", "West", "Southwest"]
CHANNELS       = ["online", "in-store", "mobile"]
CATEGORIES     = ["Electronics", "Apparel", "Home & Garden", "Sports", "Beauty"]
SEGMENTS       = ["new", "returning", "vip"]
STATUSES       = ["completed", "completed", "completed", "cancelled", "returned"]

random.seed(SEED)

def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

# ── Dimension: customers ──────────────────────────────────────────────────────
customers = []
for _ in range(N_CUSTOMERS):
    customers.append({
        "CUSTOMER_ID":  str(uuid.uuid4()),
        "SIGNUP_DATE":  rand_date(date(2022, 1, 1), START_DATE).isoformat(),
        "SEGMENT":      random.choice(SEGMENTS),
        "CITY":         random.choice(["Austin", "Dallas", "Houston", "Denver",
                                       "Chicago", "NYC", "LA", "Seattle"]),
        "STATE":        random.choice(["TX", "CO", "IL", "NY", "CA", "WA"]),
        "COUNTRY":      "US",
    })
df_customers = pd.DataFrame(customers)

# ── Dimension: products ───────────────────────────────────────────────────────
products = []
for i in range(N_PRODUCTS):
    cat   = random.choice(CATEGORIES)
    cost  = round(random.uniform(5, 150), 2)
    margin = random.uniform(0.3, 0.7)
    products.append({
        "PRODUCT_ID":   str(uuid.uuid4()),
        "PRODUCT_NAME": f"{cat} Item {i+1:03d}",
        "CATEGORY":     cat,
        "SUBCATEGORY":  f"{cat} Sub {random.randint(1,3)}",
        "BRAND":        random.choice(["BrandA","BrandB","BrandC","BrandD"]),
        "COST_PRICE":   cost,
        "LIST_PRICE":   round(cost / (1 - margin), 2),
    })
df_products = pd.DataFrame(products)

# ── Fact: orders + order_items ────────────────────────────────────────────────
orders, order_items = [], []
cust_ids = [c["CUSTOMER_ID"] for c in customers]
prod_list = products

for _ in range(N_ORDERS):
    oid        = str(uuid.uuid4())
    cid        = random.choice(cust_ids)
    odate      = rand_date(START_DATE, END_DATE)
    status     = random.choice(STATUSES)
    channel    = random.choice(CHANNELS)
    region     = random.choice(REGIONS)
    n_items    = random.randint(1, 6)

    gross, discount, shipping = 0.0, 0.0, 0.0
    for _ in range(n_items):
        prod    = random.choice(prod_list)
        qty     = random.randint(1, 4)
        disc_r  = random.choice([0.0, 0.0, 0.05, 0.10, 0.15])
        line    = round(prod["LIST_PRICE"] * qty, 2)
        disc    = round(line * disc_r, 2)
        order_items.append({
            "ITEM_ID":      str(uuid.uuid4()),
            "ORDER_ID":     oid,
            "PRODUCT_ID":   prod["PRODUCT_ID"],
            "PRODUCT_NAME": prod["PRODUCT_NAME"],
            "CATEGORY":     prod["CATEGORY"],
            "QUANTITY":     qty,
            "UNIT_PRICE":   prod["LIST_PRICE"],
            "COST_PRICE":   prod["COST_PRICE"],
        })
        gross   += line
        discount+= disc

    shipping = round(random.uniform(0, 15) if channel != "in-store" else 0, 2)
    orders.append({
        "ORDER_ID":       oid,
        "CUSTOMER_ID":    cid,
        "ORDER_DATE":     odate.isoformat(),
        "STATUS":         status,
        "CHANNEL":        channel,
        "REGION":         region,
        "STORE_ID":       f"STR{random.randint(1,10):02d}",
        "GROSS_REVENUE":  round(gross, 2),
        "DISCOUNT_AMOUNT":round(discount, 2),
        "SHIPPING_COST":  shipping,
        "ITEM_COUNT":     n_items,
    })

df_orders = pd.DataFrame(orders)
df_items  = pd.DataFrame(order_items)

print(f"Generated: {len(df_customers)} customers, {len(df_products)} products, "
      f"{len(df_orders)} orders, {len(df_items)} order items")

# ── Load to Snowflake ─────────────────────────────────────────────────────────
def get_conn():
    return snowflake.connector.connect(
        account  = os.environ["SNOWFLAKE_ACCOUNT"],
        user     = os.environ["SNOWFLAKE_USER"],
        password = os.environ["SNOWFLAKE_PASSWORD"],
        role     = "TRANSFORMER",
        warehouse= "COMPUTE_WH",
        database = "RETAIL_BI",
        schema   = "RAW",
    )

TABLE_MAP = {
    "RAW_CUSTOMERS":    df_customers,
    "RAW_PRODUCTS":     df_products,
    "RAW_ORDERS":       df_orders,
    "RAW_ORDER_ITEMS":  df_items,
}

conn = get_conn()
for table, df in TABLE_MAP.items():
    print(f"Loading {table} ({len(df)} rows)...", end=" ")
    success, nchunks, nrows, _ = write_pandas(
        conn, df, table,
        database="RETAIL_BI", schema="RAW",
        overwrite=True, auto_create_table=False,
    )
    print(f"{'OK' if success else 'FAILED'} ({nrows} rows, {nchunks} chunks)")

conn.close()
print("Done.")
