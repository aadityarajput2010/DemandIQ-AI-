
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_DIR / "data" / "processed" / "sales_long_sample.csv"
MODEL_FILE = PROJECT_DIR / "models" / "multi_product_random_forest.joblib"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "multi_product_forecast.csv"

FORECAST_DAYS = 28

# Load historical sales and trained model
data = pd.read_csv(DATA_FILE)
model = joblib.load(MODEL_FILE)

# Convert day labels into numbers
data["day_number"] = (
    data["day"].str.replace("d_", "", regex=False).astype(int)
)

data = data.sort_values(
    ["item_id", "store_id", "day_number"]
)

forecast_results = []

# Generate forecasts separately for each product and store
for (item_id, store_id), group in data.groupby(
    ["item_id", "store_id"]
):
    group = group.sort_values("day_number")

    history = group["sales"].astype(float).tolist()
    last_day = int(group["day_number"].max())

    # Check sufficient history
    if len(history) < 7:
        print(f"Skipping {item_id}: insufficient history")
        continue

    # Generate 28 future days
    for step in range(1, FORECAST_DAYS + 1):

        next_day = last_day + step

        # Prepare all features expected by the Pipeline
        features = pd.DataFrame([{
            "lag_1": history[-1],
            "lag_7": history[-7],
            "rolling_mean_7": np.mean(history[-7:]),
            "day_of_week": (next_day - 1) % 7,
            "is_weekend": int((next_day - 1) % 7 in [5, 6]),
            "item_id": item_id,
            "store_id": store_id
        }])

        # Predict next day's sales
        prediction = max(
            0,
            float(model.predict(features)[0])
        )

        forecast_results.append({
            "item_id": item_id,
            "store_id": store_id,
            "day_number": next_day,
            "forecast_sales": round(prediction, 2)
        })

        # Use prediction as history for next day
        history.append(prediction)

# Create forecast DataFrame
forecast_df = pd.DataFrame(forecast_results)

# Save forecast
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
forecast_df.to_csv(OUTPUT_FILE, index=False)

# Display results
print("\nDEMANDIQ AI - PRODUCT-AWARE 28-DAY FORECAST")
print("-------------------------------------------")

print("Products:", forecast_df["item_id"].nunique())
print("Stores:", forecast_df["store_id"].nunique())
print("Forecast records:", len(forecast_df))
print("Forecast days:", FORECAST_DAYS)

print("\nTotal forecast demand:",
      round(forecast_df["forecast_sales"].sum(), 2))

print("\nForecast saved to:", OUTPUT_FILE)

print("\nForecast preview:")
print(forecast_df.head(10).to_string(index=False))
