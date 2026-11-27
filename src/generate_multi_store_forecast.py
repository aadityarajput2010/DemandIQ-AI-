
import pandas as pd
import joblib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

history_file = (
    PROJECT_DIR / "data" / "processed"
    / "sales_long_multi_store_sample.csv"
)

model_file = (
    PROJECT_DIR / "models"
    / "multi_store_random_forest.joblib"
)

output_file = (
    PROJECT_DIR / "data" / "processed"
    / "multi_store_forecast.csv"
)

FORECAST_DAYS = 28

print("DemandIQ AI - Optimized Multi-Store Forecast")
print("-" * 55)

# Load historical data and trained model
history = pd.read_csv(history_file)
model = joblib.load(model_file)

history["day_number"] = (
    history["day"].str.replace("d_", "", regex=False).astype(int)
)

# Sort historical records
history = history.sort_values(
    ["item_id", "store_id", "day_number"]
)

# Prepare independent history for each product-store combination
states = []

for (item_id, store_id), group in history.groupby(
    ["item_id", "store_id"]
):
    sales_history = group["sales"].astype(float).tolist()

    states.append({
        "item_id": item_id,
        "store_id": store_id,
        "sales_history": sales_history,
        "day_number": int(group["day_number"].max())
    })

print("Product-store combinations:", len(states))
print("Starting batch forecasting...")

forecast_results = []

# Predict one complete day at a time
for forecast_step in range(1, FORECAST_DAYS + 1):

    batch = []

    for state in states:
        sales_history = state["sales_history"]
        next_day = state["day_number"] + 1

        batch.append({
            "item_id": state["item_id"],
            "store_id": state["store_id"],
            "lag_1": sales_history[-1],
            "lag_7": sales_history[-7],
            "rolling_mean_7": sum(sales_history[-7:]) / 7,
            "day_of_week": (next_day - 1) % 7,
            "is_weekend": int((next_day - 1) % 7 >= 5)
        })

    # Predict all product-store combinations together
    batch_df = pd.DataFrame(batch)

    predictions = model.predict(batch_df)

    # Save predictions and update each history
    for state, prediction in zip(states, predictions):

        predicted_sales = max(0.0, float(prediction))

        next_day = state["day_number"] + 1

        forecast_results.append({
            "item_id": state["item_id"],
            "store_id": state["store_id"],
            "day_number": next_day,
            "predicted_sales": predicted_sales
        })

        state["sales_history"].append(predicted_sales)
        state["day_number"] = next_day

    print(f"Completed forecast day {forecast_step}/{FORECAST_DAYS}")

# Create and save forecast dataset
forecast_df = pd.DataFrame(forecast_results)

forecast_df.to_csv(output_file, index=False)

print("-" * 55)
print("Multi-store forecast generated successfully!")
print("Forecast records:", len(forecast_df))
print("Unique products:", forecast_df["item_id"].nunique())
print("Unique stores:", forecast_df["store_id"].nunique())

print(
    "Product-store combinations:",
    forecast_df[["item_id", "store_id"]]
    .drop_duplicates().shape[0]
)

print("Forecast days:", forecast_df["day_number"].nunique())

print(
    "Total predicted demand:",
    round(forecast_df["predicted_sales"].sum(), 2)
)

print("Saved to:", output_file)
