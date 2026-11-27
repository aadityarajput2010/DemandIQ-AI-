
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_DIR / "data" / "raw" / "sales_train_validation.csv"
FORECAST_FILE = PROJECT_DIR / "data" / "processed" / "multi_product_forecast.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "multi_product_inventory.csv"

# Inventory assumptions (simulated)
LEAD_TIME_DAYS = 5
SERVICE_LEVEL_Z = 1.65
TARGET_STOCK_DAYS = 14

# Load historical sales
sales = pd.read_csv(RAW_FILE)

sample = sales.drop_duplicates(subset=["item_id"]).head(10).copy()

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

records = []

for _, product in sample.iterrows():
    daily_sales = product[daily_columns].astype(float)

    records.append({
        "item_id": product["item_id"],
        "department": product["dept_id"],
        "category": product["cat_id"],
        "store_id": product["store_id"],
        "average_daily_demand": daily_sales.mean(),
        "daily_demand_std": daily_sales.std(),
        "total_historical_sales": int(daily_sales.sum())
    })

inventory = pd.DataFrame(records)

# Load and summarize the 28-day forecasts
forecast = pd.read_csv(FORECAST_FILE)

forecast_summary = (
    forecast.groupby(["item_id", "store_id"], as_index=False)
    .agg(
        forecast_28_day_demand=("forecast_sales", "sum"),
        average_forecast_daily_demand=("forecast_sales", "mean")
    )
)

inventory = inventory.merge(
    forecast_summary,
    on=["item_id", "store_id"],
    how="left"
)

# Use forecast demand for inventory planning
inventory["planning_daily_demand"] = (
    inventory["average_forecast_daily_demand"]
)

# Simulated inventory values
inventory["current_stock"] = 60
inventory["stock_on_order"] = 20
inventory["reserved_stock"] = 10

inventory["net_stock_position"] = (
    inventory["current_stock"]
    + inventory["stock_on_order"]
    - inventory["reserved_stock"]
)

# Calculate forecast-based lead-time demand
inventory["expected_lead_time_demand"] = (
    inventory["planning_daily_demand"] * LEAD_TIME_DAYS
)

# Calculate safety stock using historical demand variation
inventory["safety_stock"] = (
    SERVICE_LEVEL_Z
    * inventory["daily_demand_std"]
    * (LEAD_TIME_DAYS ** 0.5)
).apply(lambda value: int(value) + (value % 1 > 0))

# Forecast-based reorder point
inventory["reorder_point"] = (
    inventory["expected_lead_time_demand"]
    + inventory["safety_stock"]
).apply(lambda value: int(value) + (value % 1 > 0))

# Forecast-based target stock
inventory["target_stock"] = (
    inventory["planning_daily_demand"] * TARGET_STOCK_DAYS
).apply(lambda value: int(value) + (value % 1 > 0))

# Calculate recommended order quantity
inventory["recommended_order_quantity"] = inventory.apply(
    lambda row: (
        max(0, row["target_stock"] - row["net_stock_position"])
        if row["net_stock_position"] <= row["reorder_point"]
        else 0
    ),
    axis=1
)

# Classify inventory status
inventory["inventory_status"] = inventory.apply(
    lambda row: (
        "REORDER REQUIRED"
        if row["net_stock_position"] <= row["reorder_point"]
        else "STOCK SUFFICIENT"
    ),
    axis=1
)

# Save recommendations
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
inventory.to_csv(OUTPUT_FILE, index=False)

print("DEMANDIQ AI - FORECAST-BASED INVENTORY OPTIMIZATION")
print("Products:", len(inventory))
print(
    "Total 28-day forecast demand:",
    round(inventory["forecast_28_day_demand"].sum(), 2)
)
print(
    "Products requiring reorder:",
    (inventory["inventory_status"] == "REORDER REQUIRED").sum()
)
print("Saved to:", OUTPUT_FILE)

print("\nInventory recommendations:")
print(
    inventory[
        [
            "item_id",
            "average_daily_demand",
            "average_forecast_daily_demand",
            "reorder_point",
            "net_stock_position",
            "recommended_order_quantity",
            "inventory_status"
        ]
    ].to_string(index=False)
)
