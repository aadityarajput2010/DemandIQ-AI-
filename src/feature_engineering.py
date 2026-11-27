
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "product_048_history.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "product_048_features.csv"

# Load historical sales
data = pd.read_csv(DATA_FILE).sort_values("day_number").copy()

# Historical sales features
data["lag_1"] = data["sales"].shift(1)
data["lag_7"] = data["sales"].shift(7)

# Shift first to prevent today's sales from entering today's features
data["rolling_mean_7"] = (
    data["sales"].shift(1).rolling(window=7).mean()
)

# Calendar features
data["day_of_week"] = (data["day_number"] - 1) % 7
data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)

# Remove rows that don't yet have enough history
features = data.dropna().copy()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
features.to_csv(OUTPUT_FILE, index=False)

print("Forecasting features created successfully!")
print("Rows before feature engineering:", len(data))
print("Rows after feature engineering:", len(features))
print("\nFeature columns:")
print(features.columns.tolist())
print("\nFeature preview:")
print(features.head().to_string(index=False))
print("\nSaved to:", OUTPUT_FILE)
