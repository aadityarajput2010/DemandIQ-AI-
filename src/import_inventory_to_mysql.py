
import pandas as pd
import mysql.connector

# Load inventory CSV
file_path = "data/processed/multi_product_inventory.csv"
df = pd.read_csv(file_path)

print("Inventory records loaded:", len(df))

# Connect to MySQL
password = input("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=password,
    database="demandiq"
)

cursor = connection.cursor()

# Insert new records or update existing records
sql = """
INSERT INTO inventory_recommendations (
    item_id,
    store_id,
    avg_daily_demand,
    forecast_daily_demand,
    lead_time_days,
    safety_stock,
    reorder_point,
    net_stock_position,
    recommended_order_qty,
    inventory_status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    avg_daily_demand = VALUES(avg_daily_demand),
    forecast_daily_demand = VALUES(forecast_daily_demand),
    lead_time_days = VALUES(lead_time_days),
    safety_stock = VALUES(safety_stock),
    reorder_point = VALUES(reorder_point),
    net_stock_position = VALUES(net_stock_position),
    recommended_order_qty = VALUES(recommended_order_qty),
    inventory_status = VALUES(inventory_status)
"""

records = []

for _, row in df.iterrows():
    records.append((
        row["item_id"],
        row["store_id"],
        float(row["average_daily_demand"]),
        float(row["average_forecast_daily_demand"]),
        5,
        float(row["safety_stock"]),
        float(row["reorder_point"]),
        float(row["net_stock_position"]),
        float(row["recommended_order_quantity"]),
        row["inventory_status"]
    ))

cursor.executemany(sql, records)
connection.commit()

print("Inventory records processed:", cursor.rowcount)

cursor.close()
connection.close()

print("Inventory import completed successfully!")
