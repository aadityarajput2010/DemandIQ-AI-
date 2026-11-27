
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Locate the project and processed dataset
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"
OUTPUT_FILE = PROJECT_DIR / "reports" / "daily_sales_trend.png"

# Load the processed sales data
sales = pd.read_csv(DATA_FILE)

# Calculate total sales for each day across all sampled products
daily_sales = (
    sales.groupby("day", as_index=False)["sales"]
    .sum()
)

# Create the sales trend chart
plt.figure(figsize=(14, 5))
plt.plot(daily_sales["day"], daily_sales["sales"])
plt.title("DemandIQ AI - Daily Sales Trend")
plt.xlabel("Day")
plt.ylabel("Total Units Sold")
plt.xticks(
    ticks=range(0, len(daily_sales), 150),
    labels=daily_sales["day"].iloc[::150],
    rotation=45
)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the chart
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()

print("Daily sales visualization created!")
print("Chart saved to:", OUTPUT_FILE)
