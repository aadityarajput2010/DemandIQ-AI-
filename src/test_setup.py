
import numpy as np
import pandas as pd

print("NumPy version:", np.__version__)
print("Pandas version:", pd.__version__)

numbers = np.array([100, 200, 300, 400, 500])

data = pd.DataFrame({
    "Sales": numbers
})

print("\nSample sales data:")
print(data)

print("\nTotal sales:", data["Sales"].sum())

print("\nDemandIQ AI data-analysis test successful!")
print("\nTotal sales:", data["Sales"].sum())