
from pathlib import Path
import pandas as pd

# Locate project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_DIR / "data" / "raw" / "sales_train_validation.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"

# Load the original sales data
sales = pd.read_csv(RAW_FILE)

# Identify daily sales columns
daily_columns = [col for col in sales.columns if col.startswith("d_")]

# Keep a manageable sample for initial development
sample = sales.head(100).copy()

# Convert daily columns into rows
sales_long = sample.melt(
    id_vars=["item_id", "dept_id", "cat_id", "store_id", "state_id"],
    value_vars=daily_columns,
    var_name="day",
    value_name="sales"
)

# Save the transformed data
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
sales_long.to_csv(OUTPUT_FILE, index=False)

# Display a summary
print("DemandIQ AI: Sales transformation complete!")
print("Products/store records:", len(sample))
print("Daily sales columns:", len(daily_columns))
print("Transformed rows:", len(sales_long))
print("Saved to:", OUTPUT_FILE)
print("\nPreview:")
print(sales_long.head())


# Verify the saved processed dataset
processed = pd.read_csv(OUTPUT_FILE)

print("\nProcessed dataset verification:")
print("Shape:", processed.shape)
print("Columns:", processed.columns.tolist())
print("Missing values:", processed.isnull().sum().sum())

# Basic sales analysis
print("\n--- DemandIQ AI: Sales Analysis ---")

print("Total units sold:", processed["sales"].sum())
print("Average units per record:", round(processed["sales"].mean(), 2))
print("Unique products:", processed["item_id"].nunique())
print("Unique stores:", processed["store_id"].nunique())

print("\nSales summary:")
print(processed["sales"].describe())