
from pathlib import Path
import pandas as pd

# Locate the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Locate the raw sales dataset
DATA_FILE = PROJECT_DIR / "data" / "raw" / "sales_train_validation.csv"

# Load the sales dataset
sales = pd.read_csv(DATA_FILE)

# Display basic information
print("DemandIQ AI - Sales Data Loaded Successfully!")
print("Dataset shape:", sales.shape)

print("\nFirst five rows:")
print(sales.head())


print("\nColumn names and data types:")
print(sales.dtypes.head(10))

print("\nFirst and last daily sales columns:")
daily_columns = [col for col in sales.columns if col.startswith("d_")]
print("First 5:", daily_columns[:5])
print("Last 5:", daily_columns[-5:])

print("\nMissing values in the first 10 columns:")
print(sales.iloc[:, :10].isnull().sum())
