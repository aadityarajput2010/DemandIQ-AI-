
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_DIR / "data" / "processed" / "product_048_features.csv"
MODEL_FILE = PROJECT_DIR / "models" / "random_forest_product_048.joblib"
OUTPUT_FILE = PROJECT_DIR / "reports" / "forecast_model_comparison.png"

data = pd.read_csv(DATA_FILE)

feature_columns = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "day_of_week",
    "is_weekend"
]

# Use the same final 28 days as the previous evaluation
split_index = len(data) - 28
train = data.iloc[:split_index]
test = data.iloc[split_index:].copy()

# Recreate baseline forecast from training data only
baseline_value = train["sales"].tail(28).mean()
test["baseline"] = baseline_value

# Load the saved Random Forest model
model = joblib.load(MODEL_FILE)

# Predict the test period
test["random_forest"] = np.maximum(
    0, model.predict(test[feature_columns])
)

# Plot all three series
plt.figure(figsize=(13, 6))

plt.plot(
    test["day_number"], test["sales"],
    marker="o", label="Actual Sales"
)
plt.plot(
    test["day_number"], test["baseline"],
    linestyle="--", label="Baseline"
)
plt.plot(
    test["day_number"], test["random_forest"],
    marker=".", label="Random Forest"
)

plt.title("DemandIQ AI - Forecast Model Comparison")
plt.xlabel("Day Number")
plt.ylabel("Units Sold")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()

print("Comparison chart saved to:", OUTPUT_FILE)
