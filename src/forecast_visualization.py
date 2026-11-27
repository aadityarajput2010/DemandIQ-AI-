
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "product_048_history.csv"
OUTPUT_FILE = PROJECT_DIR / "reports" / "baseline_forecast_comparison.png"

data = pd.read_csv(DATA_FILE)

# Keep the same final 28 days used to evaluate the baseline
train = data.iloc[:-28]
test = data.iloc[-28:].copy()

# Recreate the baseline forecast
forecast_value = train["sales"].tail(28).mean()
test["predicted_sales"] = forecast_value

# Plot actual versus predicted sales
plt.figure(figsize=(12, 5))

plt.plot(
    test["day_number"],
    test["sales"],
    marker="o",
    label="Actual Sales"
)

plt.plot(
    test["day_number"],
    test["predicted_sales"],
    linestyle="--",
    label="Baseline Forecast"
)

plt.title("DemandIQ AI - Actual vs Baseline Forecast")
plt.xlabel("Day Number")
plt.ylabel("Units Sold")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()

print("Forecast comparison chart saved to:", OUTPUT_FILE)
