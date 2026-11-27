
import pandas as pd
from pathlib import Path

# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Input and output paths
input_file = PROJECT_DIR / "data" / "raw" / "sales_train_validation.csv"
output_file = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "sales_long_multi_store_sample.csv"
)

print("DemandIQ AI - Multi-Store Dataset Preparation")
print("-" * 50)

# Load original dataset
df = pd.read_csv(input_file)

print("Original dataset loaded:", df.shape)

# Select the first 100 unique products
selected_products = df["item_id"].drop_duplicates().head(100)

# Include these products across all available stores
sample = df[df["item_id"].isin(selected_products)].copy()

print("Selected product-store records:", len(sample))
print("Unique products:", sample["item_id"].nunique())
print("Unique stores:", sample["store_id"].nunique())

# Identify daily sales columns
sales_columns = [
    column for column in sample.columns
    if column.startswith("d_")
]

# Convert wide format into long format
sales_long = sample.melt(
    id_vars=[
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id"
    ],
    value_vars=sales_columns,
    var_name="day",
    value_name="sales"
)

# Save processed dataset
sales_long.to_csv(output_file, index=False)

print("-" * 50)
print("Multi-store dataset prepared successfully!")
print("Total daily records:", len(sales_long))
print("Unique products:", sales_long["item_id"].nunique())
print("Unique stores:", sales_long["store_id"].nunique())
print("Output saved to:", output_file)

