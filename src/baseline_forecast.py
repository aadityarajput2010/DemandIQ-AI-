
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "product_048_history.csv"

# Load the product's daily sales history
data = pd.read_csv(DATA_FILE)

# Reserve the last 28 days for testing
train = data.iloc[:-28].copy()
test = data.iloc[-28:].copy()

# Baseline: predict each test day using the average
# sales from the last 28 days of training data
forecast_value = train["sales"].tail(28).mean()

# Make one prediction for each of the 28 test days
predictions = np.full(len(test), forecast_value)

# Evaluate predictions against actual sales
mae = mean_absolute_error(test["sales"], predictions)
rmse = np.sqrt(mean_squared_error(test["sales"], predictions))

print("DEMANDIQ AI - BASELINE FORECAST")
print("Product: HOBBIES_1_048")
print("Training days:", len(train))
print("Testing days:", len(test))
print("Forecast per day:", round(forecast_value, 2))
print("Actual average sales in test period:", round(test["sales"].mean(), 2))
print("Mean Absolute Error (MAE):", round(mae, 2))
print("Root Mean Squared Error (RMSE):", round(rmse, 2))

# Display actual versus predicted sales
comparison = test[["day_number", "sales"]].copy()
comparison = comparison.rename(columns={"sales": "actual_sales"})
comparison["predicted_sales"] = np.round(predictions, 2)

print("\nFirst 10 test predictions:")
print(comparison.head(10).to_string(index=False))
