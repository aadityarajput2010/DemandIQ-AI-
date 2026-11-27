
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "product_048_features.csv"
MODEL_FILE = PROJECT_DIR / "models" / "random_forest_product_048.joblib"

data = pd.read_csv(DATA_FILE)

# Features used to predict sales
feature_columns = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "day_of_week",
    "is_weekend"
]

X = data[feature_columns]
y = data["sales"]

# Keep the final 28 days for testing
split_index = len(data) - 28

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

# Train the model
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate predictions
predictions = np.maximum(0, model.predict(X_test))

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print("DEMANDIQ AI - RANDOM FOREST MODEL")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("Actual test average:", round(y_test.mean(), 2))
print("Predicted test average:", round(predictions.mean(), 2))

# Save the trained model
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_FILE)

print("\nModel saved to:", MODEL_FILE)
