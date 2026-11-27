
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"
OUTPUT_FILE = PROJECT_DIR / "reports" / "top_10_products.png"

# Load sales data
sales = pd.read_csv(DATA_FILE)

# Calculate total units sold for each product
product_sales = (
    sales.groupby("item_id", as_index=False)["sales"]
    .sum()
    .sort_values("sales", ascending=False)
)

# Select the top 10 products
top_10 = product_sales.head(10)

print("Top 10 Best-Selling Products")
print(top_10.to_string(index=False))

# Create a horizontal bar chart
plt.figure(figsize=(10, 6))
plt.barh(top_10["item_id"], top_10["sales"])
plt.title("DemandIQ AI - Top 10 Best-Selling Products")
plt.xlabel("Total Units Sold")
plt.ylabel("Product")
plt.gca().invert_yaxis()
plt.tight_layout()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()

print("\nChart saved to:", OUTPUT_FILE)
