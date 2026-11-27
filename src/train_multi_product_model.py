
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_DIR / "data" / "processed" / "multi_product_features.csv"
MODEL_FILE = PROJECT_DIR / "models" / "multi_product_random_forest.joblib"
REPORT_FILE = PROJECT_DIR / "reports" / "multi_product_model_metrics.csv"
FEATURE_REPORT_FILE = PROJECT_DIR / "reports" / "feature_importance.csv"
PRODUCT_REPORT_FILE = PROJECT_DIR / "reports" / "product_forecast_errors.csv"

# Load dataset
data = pd.read_csv(DATA_FILE)

# Features
numeric_features = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "day_of_week",
    "is_weekend"
]

categorical_features = [
    "item_id",
    "store_id"
]

feature_columns = numeric_features + categorical_features

# Check required columns
required_columns = feature_columns + ["day_number", "sales"]
missing_columns = [c for c in required_columns if c not in data.columns]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Chronological split
split_day = int(data["day_number"].max() * 0.8)

train_data = data[data["day_number"] <= split_day].copy()
test_data = data[data["day_number"] > split_day].copy()

X_train = train_data[feature_columns]
X_test = test_data[feature_columns]

y_train = train_data["sales"]
y_test = test_data["sales"]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", "passthrough", numeric_features),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

# Complete model pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("random_forest", RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    ))
])

# Train
model.fit(X_train, y_train)

# Predict
predictions = np.maximum(0, model.predict(X_test))

# Evaluation
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

actual_average = y_test.mean()
predicted_average = predictions.mean()

print("\nDEMANDIQ AI - PRODUCT-AWARE RANDOM FOREST")
print("-----------------------------------------")
print("Products:", data["item_id"].nunique())
print("Stores:", data["store_id"].nunique())
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("MAE:", round(mae, 3))
print("RMSE:", round(rmse, 3))
print("R2 Score:", round(r2, 3))
print("Actual average sales:", round(actual_average, 3))
print("Predicted average sales:", round(predicted_average, 3))

# Save complete pipeline
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_FILE)

# Save metrics
metrics = pd.DataFrame({
    "metric": [
        "Products",
        "Stores",
        "Training Records",
        "Testing Records",
        "MAE",
        "RMSE",
        "R2 Score",
        "Actual Average Sales",
        "Predicted Average Sales"
    ],
    "value": [
        data["item_id"].nunique(),
        data["store_id"].nunique(),
        len(X_train),
        len(X_test),
        round(mae, 3),
        round(rmse, 3),
        round(r2, 3),
        round(actual_average, 3),
        round(predicted_average, 3)
    ]
})

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
metrics.to_csv(REPORT_FILE, index=False)

# Feature importance
forest = model.named_steps["random_forest"]
encoded_names = model.named_steps["preprocessor"].get_feature_names_out()

importance = pd.DataFrame({
    "feature": encoded_names,
    "importance": forest.feature_importances_
}).sort_values("importance", ascending=False)

importance.to_csv(FEATURE_REPORT_FILE, index=False)

# Product-wise error
test_results = test_data[["item_id", "sales"]].copy()
test_results["predicted_sales"] = predictions
test_results["absolute_error"] = (
    test_results["sales"] - test_results["predicted_sales"]
).abs()

product_errors = (
    test_results.groupby("item_id")
    .agg(
        actual_average_sales=("sales", "mean"),
        predicted_average_sales=("predicted_sales", "mean"),
        product_MAE=("absolute_error", "mean"),
        test_records=("sales", "count")
    )
    .reset_index()
    .sort_values("product_MAE", ascending=False)
)

product_errors.to_csv(PRODUCT_REPORT_FILE, index=False)

print("\nTOP 10 PRODUCTS WITH HIGHEST ERROR")
print("----------------------------------")
print(product_errors.head(10).to_string(index=False))

print("\nModel saved:", MODEL_FILE)
print("Metrics saved:", REPORT_FILE)
print("Feature importance saved:", FEATURE_REPORT_FILE)
print("Product errors saved:", PRODUCT_REPORT_FILE)
