import pandas as pd
import mysql.connector

# Load product information
file_path = "data/processed/multi_product_inventory.csv"
df = pd.read_csv(file_path)

# Keep only product details
products = df[
    ["item_id", "store_id", "category", "department"]
].drop_duplicates()

password = input("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=password,
    database="demandiq"
)

cursor = connection.cursor()

sql = """
INSERT INTO products
(item_id, store_id, category, department, state_id)
VALUES (%s, %s, %s, %s, %s)
"""

records = [
    (
        row["item_id"],
        row["store_id"],
        row["category"],
        row["department"],
        "CA"
    )
    for _, row in products.iterrows()
]

cursor.executemany(sql, records)
connection.commit()

print("Product records inserted:", cursor.rowcount)

cursor.close()
connection.close()

print("Product import completed successfully!")