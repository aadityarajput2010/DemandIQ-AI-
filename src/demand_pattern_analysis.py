
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"
OUTPUT_FILE = PROJECT_DIR / "reports" / "demand_pattern_analysis.png"

sales = pd.read_csv(DATA_FILE)

# Calculate daily demand across the sampled products
daily_sales = sales.groupby("day")["sales"].sum()

# Count days with and without sales
zero_sales_days = (daily_sales == 0).sum()
positive_sales_days = (daily_sales > 0).sum()

print("DEMAND PATTERN ANALYSIS")
print("Total days:", len(daily_sales))
print("Days with zero total sales:", zero_sales_days)
print("Days with positive total sales:", positive_sales_days)
print("Highest daily sales:", daily_sales.max())
print("Lowest daily sales:", daily_sales.min())

# Plot the distribution of daily demand
plt.figure(figsize=(10, 5))
plt.hist(daily_sales, bins=30, edgecolor="black")
plt.title("DemandIQ AI - Distribution of Daily Sales")
plt.xlabel("Total Units Sold per Day")
plt.ylabel("Number of Days")
plt.tight_layout()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()

print("\nChart saved to:", OUTPUT_FILE)
