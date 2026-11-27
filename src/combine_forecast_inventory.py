
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

FORECAST_FILE = (
    PROJECT_DIR / "data" / "processed" / "multi_product_forecast.csv"
)
INVENTORY_FILE = (
    PROJECT_DIR / "data" / "processed" / "multi_product_inventory.csv"
)
OUTPUT_FILE = (
    PROJECT_DIR / "data" / "processed" / "forecast_inventory_summary.csv"
)

# Load forecast and inventory data
forecast = pd.read_csv(FORECAST_FILE)
inventory = pd.read_csv(INVENTORY_FILE)

# Calculate total forecast demand over the next 28 days
forecast_summary = (
    forecast.groupby(["item_id", "store_id"], as_index=False)
    .agg(
        forecast_28_day_demand=("forecast_sales", "sum"),
        average_forecast_daily_demand=("forecast_sales", "mean"),
    )
)

# Combine forecast and inventory information
summary = inventory.merge(
    forecast_summary,
    on=["item_id", "store_id"],
    how="left",
)

# Round forecast values
summary["forecast_28_day_demand"] = (
    summary["forecast_28_day_demand"].round(2)
)
summary["average_forecast_daily_demand"] = (
    summary["average_forecast_daily_demand"].round(2)
)

# Save the combined report
summary.to_csv(OUTPUT_FILE, index=False)

print("DEMANDIQ AI - FORECAST AND INVENTORY SUMMARY")
print("Products:", summary["item_id"].nunique())
print("Total 28-day forecast demand:",
      round(summary["forecast_28_day_demand"].sum(), 2))
print("Products requiring reorder:",
      (summary["inventory_status"] == "REORDER REQUIRED").sum())
print("Saved to:", OUTPUT_FILE)

print("\nSummary preview:")
print(
    summary[
        [
            "item_id",
            "forecast_28_day_demand",
            "reorder_point",
            "net_stock_position",
            "recommended_order_quantity",
            "inventory_status",
        ]
    ].head(10).to_string(index=False)
)
