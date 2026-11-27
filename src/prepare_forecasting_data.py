
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "product_048_history.csv"

sales = pd.read_csv(DATA_FILE)

# Select the highest-selling product from our analysis
product_id = "HOBBIES_1_048"

product_data = sales[sales["item_id"] == product_id].copy()

# Convert day labels such as d_1 and d_2 into numeric day numbers
product_data["day_number"] = (
    product_data["day"].str.replace("d_", "", regex=False).astype(int)
)

# Sort chronologically
product_data = product_data.sort_values("day_number")

# Keep only the columns needed for forecasting
forecast_data = product_data[["day_number", "sales"]].copy()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
forecast_data.to_csv(OUTPUT_FILE, index=False)

print("Forecasting data prepared!")
print("Product:", product_id)
print("Number of daily records:", len(forecast_data))
print("Total units sold:", forecast_data["sales"].sum())
print("\nFirst 5 days:")
print(forecast_data.head().to_string(index=False))
print("\nLast 5 days:")
print(forecast_data.tail().to_string(index=False))
print("\nSaved to:", OUTPUT_FILE)
