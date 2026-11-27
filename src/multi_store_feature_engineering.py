
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

input_file = (
    PROJECT_DIR / "data" / "processed"
    / "sales_long_multi_store_sample.csv"
)

output_file = (
    PROJECT_DIR / "data" / "processed"
    / "multi_store_features.csv"
)

print("DemandIQ AI - Multi-Store Feature Engineering")
print("-" * 55)

# Load multi-store sales data
df = pd.read_csv(input_file)

print("Dataset loaded:", df.shape)

# Convert day labels such as d_1, d_2 into numbers
df["day_number"] = (
    df["day"].str.replace("d_", "", regex=False).astype(int)
)

# Sort each product-store history chronologically
df = df.sort_values(
    ["item_id", "store_id", "day_number"]
).reset_index(drop=True)

# Create features separately for each product in each store
groups = df.groupby(["item_id", "store_id"])["sales"]

df["lag_1"] = groups.shift(1)
df["lag_7"] = groups.shift(7)

# Average demand over the previous 7 days
df["rolling_mean_7"] = (
    df.groupby(["item_id", "store_id"])["sales"]
    .transform(lambda series: series.shift(1).rolling(7).mean())
)

# Calendar features
df["day_of_week"] = (df["day_number"] - 1) % 7
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

# Remove rows without sufficient historical data
df = df.dropna(
    subset=["lag_1", "lag_7", "rolling_mean_7"]
).copy()

# Save engineered dataset
df.to_csv(output_file, index=False)

print("-" * 55)
print("Multi-store feature engineering completed!")
print("Feature dataset shape:", df.shape)
print("Unique products:", df["item_id"].nunique())
print("Unique stores:", df["store_id"].nunique())
print("Product-store combinations:",
      df[["item_id", "store_id"]].drop_duplicates().shape[0])
print("Output saved to:", output_file)
