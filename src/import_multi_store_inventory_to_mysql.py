from pathlib import Path
import pandas as pd
import mysql.connector

PROJECT_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "multi_store_inventory.csv"
)

# Load multi-store inventory data
df = pd.read_csv(FILE_PATH)

print("Inventory rows loaded:", len(df))

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=input("Enter your MySQL root password: "),
    database="demandiq"
)

cursor = connection.cursor()

sql = """
INSERT INTO multi_store_inventory_recommendations (
    item_id,
    store_id,
    average_historical_demand,
    demand_std,
    average_forecast_demand,
    total_forecast_demand,
    safety_stock,
    lead_time_demand,
    reorder_point,
    current_stock,
    stock_on_order,
    reserved_stock,
    net_stock_position,
    target_stock,
    status,
    recommended_order_qty
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE
    average_historical_demand = VALUES(average_historical_demand),
    demand_std = VALUES(demand_std),
    average_forecast_demand = VALUES(average_forecast_demand),
    total_forecast_demand = VALUES(total_forecast_demand),
    safety_stock = VALUES(safety_stock),
    lead_time_demand = VALUES(lead_time_demand),
    reorder_point = VALUES(reorder_point),
    current_stock = VALUES(current_stock),
    stock_on_order = VALUES(stock_on_order),
    reserved_stock = VALUES(reserved_stock),
    net_stock_position = VALUES(net_stock_position),
    target_stock = VALUES(target_stock),
    status = VALUES(status),
    recommended_order_qty = VALUES(recommended_order_qty)
"""

records = [
    (
        row["item_id"],
        row["store_id"],
        float(row["average_historical_demand"]),
        float(row["demand_std"]),
        float(row["average_forecast_demand"]),
        float(row["total_forecast_demand"]),
        float(row["safety_stock"]),
        float(row["lead_time_demand"]),
        float(row["reorder_point"]),
        float(row["current_stock"]),
        float(row["stock_on_order"]),
        float(row["reserved_stock"]),
        float(row["net_stock_position"]),
        float(row["target_stock"]),
        row["status"],
        float(row["recommended_order_qty"])
    )
    for _, row in df.iterrows()
]

try:
    cursor.executemany(sql, records)
    connection.commit()

    print("Multi-store inventory import completed.")
    print("Rows affected:", cursor.rowcount)
    print("Inventory records processed:", len(records))

except mysql.connector.Error as error:
    connection.rollback()
    print("MySQL error:", error)

finally:
    cursor.close()
    connection.close()

print("Import process finished.")