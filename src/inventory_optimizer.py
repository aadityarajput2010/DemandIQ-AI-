
from math import ceil, sqrt
from pathlib import Path
import pandas as pd
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "product_048_history.csv"
)

sales_data = pd.read_csv(DATA_FILE)
daily_sales = sales_data["sales"]

average_daily_demand = daily_sales.mean()
daily_demand_std = daily_sales.std()

print("Historical sales data loaded for inventory optimization.")

def calculate_reorder_point(
    average_daily_demand,
    daily_demand_std,
    lead_time_days,
    service_level_z=1.65
):
    """
    Calculate reorder point using demand variability
    and a fixed supplier lead time.
    """
    expected_lead_time_demand = (
        average_daily_demand * lead_time_days
    )

    safety_stock = (
        service_level_z
        * daily_demand_std
        * sqrt(lead_time_days)
    )

    reorder_point = ceil(
        expected_lead_time_demand + safety_stock
    )

    return {
        "expected_lead_time_demand": round(
            expected_lead_time_demand, 2
        ),
        "safety_stock": ceil(safety_stock),
        "reorder_point": reorder_point
    }


# Example scenario for testing the inventory logic
result = calculate_reorder_point(
    average_daily_demand=average_daily_demand,
    daily_demand_std=daily_demand_std,
    lead_time_days=5
)

print("DEMANDIQ AI - INVENTORY OPTIMIZATION")
print("Expected lead-time demand:",
      result["expected_lead_time_demand"])
print("Safety stock:", result["safety_stock"])
print("Reorder point:", result["reorder_point"])


def calculate_order_quantity(
    net_stock_position,
    reorder_point,
    target_stock
):
    """Calculate order quantity using the net stock position."""
    if net_stock_position > reorder_point:
        return 0

    return max(0, ceil(target_stock - net_stock_position))

# Example inventory scenario
current_stock = 60
stock_on_order = 20
reserved_stock = 10

net_stock_position = (
    current_stock
    + stock_on_order
    - reserved_stock
)
target_stock = ceil(average_daily_demand * 14)

order_quantity = calculate_order_quantity(
    net_stock_position=net_stock_position,
    reorder_point=result["reorder_point"],
    target_stock=target_stock
)

print("Stock on order:", stock_on_order)
print("Reserved stock:", reserved_stock)
print("Net stock position:", net_stock_position)
print("Target stock:", target_stock)
print("Recommended order quantity:", order_quantity)

# Save inventory recommendation for Power BI and Streamlit
OUTPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "inventory_recommendation.csv"
)

recommendation = pd.DataFrame([{
    "item_id": "HOBBIES_1_048",
    "average_daily_demand": round(average_daily_demand, 2),
    "lead_time_days": 5,
    "safety_stock": result["safety_stock"],
    "reorder_point": result["reorder_point"],
    "current_stock": current_stock,
    "stock_on_order": stock_on_order,
    "reserved_stock": reserved_stock,
    "net_stock_position": net_stock_position,
    "target_stock": target_stock,
    "recommended_order_quantity": order_quantity
}])

recommendation.to_csv(OUTPUT_FILE, index=False)
# Classify inventory risk
if net_stock_position <= result["reorder_point"]:
    inventory_status = "REORDER REQUIRED"
else:
    inventory_status = "STOCK SUFFICIENT"

recommendation["inventory_status"] = inventory_status
recommendation.to_csv(OUTPUT_FILE, index=False)

print("Inventory status:", inventory_status)

print("\nInventory recommendation saved to:")
print(OUTPUT_FILE)

