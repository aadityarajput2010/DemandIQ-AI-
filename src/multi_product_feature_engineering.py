
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "sales_long_sample.csv"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "multi_product_features.csv"
)

# Load sales data
data = pd.read_csv(INPUT_FILE)

# Sort sales separately for each product and store
data["day_number"] = (
    data["day"].str.replace("d_", "", regex=False).astype(int)
)

data = data.sort_values(
    ["item_id", "store_id", "day_number"]
).copy()

# Create features separately for each product and store
grouped = data.groupby(["item_id", "store_id"])["sales"]

data["lag_1"] = grouped.shift(1)
data["lag_7"] = grouped.shift(7)

data["rolling_mean_7"] = grouped.transform(
    lambda series: series.shift(1).rolling(7).mean()
)

# Calendar features
data["day_of_week"] = (data["day_number"] - 1) % 7
data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)

# Remove rows without sufficient historical data
features = data.dropna().copy()

# Save processed features
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
features.to_csv(OUTPUT_FILE, index=False)

print("DEMANDIQ AI - MULTI-PRODUCT FEATURE ENGINEERING")
print("Products:", features["item_id"].nunique())
print("Stores:", features["store_id"].nunique())
print("Total feature records:", len(features))
print("Saved to:", OUTPUT_FILE)

print("\nFeature preview:")
print(features.head().to_string(index=False))
