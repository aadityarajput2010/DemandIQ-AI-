
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

history_file = (
    PROJECT_DIR / "data" / "processed"
    / "sales_long_multi_store_sample.csv"
)

forecast_file = (
    PROJECT_DIR / "data" / "processed"
    / "multi_store_forecast.csv"
)

output_file = (
    PROJECT_DIR / "data" / "processed"
    / "multi_store_inventory.csv"
)

# Inventory assumptions (simulated)
LEAD_TIME_DAYS = 5
SERVICE_FACTOR = 1.65
TARGET_STOCK_DAYS = 14

CURRENT_STOCK = 60
STOCK_ON_ORDER = 20
RESERVED_STOCK = 10

print("DemandIQ AI - Multi-Store Inventory Optimization")
print("-" * 60)

# Load historical sales and forecasts
history = pd.read_csv(history_file)
forecast = pd.read_csv(forecast_file)

# Calculate historical demand statistics
historical_stats = (
    history.groupby(["item_id", "store_id"])["sales"]
    .agg(
        average_historical_demand="mean",
        demand_std="std"
    )
    .reset_index()
)

historical_stats["demand_std"] = (
    historical_stats["demand_std"].fillna(0)
)

# Calculate forecast demand statistics
forecast_stats = (
    forecast.groupby(["item_id", "store_id"])["predicted_sales"]
    .agg(
        average_forecast_demand="mean",
        total_forecast_demand="sum"
    )
    .reset_index()
)

# Combine historical and forecast statistics
inventory = historical_stats.merge(
    forecast_stats,
    on=["item_id", "store_id"],
    how="inner"
)

# Calculate safety stock
inventory["safety_stock"] = (
    SERVICE_FACTOR
    * inventory["demand_std"]
    * np.sqrt(LEAD_TIME_DAYS)
)

# Calculate lead-time demand and reorder point
inventory["lead_time_demand"] = (
    inventory["average_forecast_demand"]
    * LEAD_TIME_DAYS
)

inventory["reorder_point"] = (
    inventory["lead_time_demand"]
    + inventory["safety_stock"]
)

# Calculate net stock position
inventory["current_stock"] = CURRENT_STOCK
inventory["stock_on_order"] = STOCK_ON_ORDER
inventory["reserved_stock"] = RESERVED_STOCK

inventory["net_stock_position"] = (
    inventory["current_stock"]
    + inventory["stock_on_order"]
    - inventory["reserved_stock"]
)

# Calculate target stock
inventory["target_stock"] = (
    inventory["average_forecast_demand"]
    * TARGET_STOCK_DAYS
    + inventory["safety_stock"]
)

# Determine reorder status
inventory["status"] = np.where(
    inventory["net_stock_position"]
    <= inventory["reorder_point"],
    "REORDER REQUIRED",
    "STOCK SUFFICIENT"
)

# Calculate recommended order quantity
inventory["recommended_order_qty"] = np.where(
    inventory["status"] == "REORDER REQUIRED",
    np.ceil(
        np.maximum(
            inventory["target_stock"]
            - inventory["net_stock_position"],
            0
        )
    ),
    0
)

# Round numerical values
numeric_columns = [
    "average_historical_demand",
    "average_forecast_demand",
    "total_forecast_demand",
    "demand_std",
    "safety_stock",
    "lead_time_demand",
    "reorder_point",
    "target_stock"
]

inventory[numeric_columns] = (
    inventory[numeric_columns].round(2)
)

# Save inventory recommendations
inventory.to_csv(output_file, index=False)

# Display summary
print("Inventory optimization completed!")
print("-" * 60)

print("Total product-store combinations:", len(inventory))

print(
    "Unique products:",
    inventory["item_id"].nunique()
)

print(
    "Unique stores:",
    inventory["store_id"].nunique()
)

print(
    "Products requiring reorder:",
    (inventory["status"] == "REORDER REQUIRED").sum()
)

print(
    "Products with sufficient stock:",
    (inventory["status"] == "STOCK SUFFICIENT").sum()
)

print(
    "Total recommended order quantity:",
    int(inventory["recommended_order_qty"].sum())
)

print(
    "Total 28-day forecast demand:",
    round(inventory["total_forecast_demand"].sum(), 2)
)

print("-" * 60)
print("Saved to:", output_file)
