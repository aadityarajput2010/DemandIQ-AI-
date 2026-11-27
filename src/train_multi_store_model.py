
import pandas as pd
import joblib
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent

input_file = (
    PROJECT_DIR / "data" / "processed"
    / "multi_store_features.csv"
)

model_file = (
    PROJECT_DIR / "models"
    / "multi_store_random_forest.joblib"
)

metrics_file = (
    PROJECT_DIR / "reports"
    / "multi_store_model_metrics.csv"
)

print("DemandIQ AI - Multi-Store Model Training")
print("-" * 55)

# Load feature dataset
df = pd.read_csv(input_file)

print("Dataset loaded:", df.shape)

# Sort chronologically
df = df.sort_values("day_number").reset_index(drop=True)

# Define features and target
categorical_features = ["item_id", "store_id"]

numeric_features = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "day_of_week",
    "is_weekend"
]

X = df[categorical_features + numeric_features]
y = df["sales"]

# Chronological train-test split
split_day = int(df["day_number"].max() * 0.8)

train_mask = df["day_number"] <= split_day
test_mask = df["day_number"] > split_day

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Split day:", split_day)

# Preprocess categorical features
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)

# Create Random Forest pipeline
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)

# Train model
print("\nTraining model...")
model.fit(X_train, y_train)

print("Model training completed!")

# Generate predictions
predictions = model.predict(X_test)

# Evaluate model
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

actual_avg = y_test.mean()
predicted_avg = predictions.mean()

print("\nMODEL PERFORMANCE")
print("-" * 55)
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2 Score: {r2:.4f}")
print(f"Actual Average Sales: {actual_avg:.4f}")
print(f"Predicted Average Sales: {predicted_avg:.4f}")

# Save trained model
joblib.dump(model, model_file)

# Save evaluation metrics
metrics = pd.DataFrame({
    "metric": [
        "MAE",
        "RMSE",
        "R2",
        "Actual Average Sales",
        "Predicted Average Sales"
    ],
    "value": [
        mae,
        rmse,
        r2,
        actual_avg,
        predicted_avg
    ]
})

metrics.to_csv(metrics_file, index=False)

print("\nModel saved to:", model_file)
print("Metrics saved to:", metrics_file)
print("\nMulti-store model training completed successfully!")
