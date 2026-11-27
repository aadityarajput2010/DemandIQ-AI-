from pathlib import Path
import pandas as pd
import mysql.connector

PROJECT_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "multi_store_forecast.csv"
)

# Load multi-store forecast data
df = pd.read_csv(FILE_PATH)

print("Forecast rows loaded:", len(df))

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=input("Enter your MySQL root password: "),
    database="demandiq"
)

cursor = connection.cursor()

sql = """
INSERT INTO multi_store_sales_forecasts
(item_id, store_id, day_number, predicted_sales)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
predicted_sales = VALUES(predicted_sales)
"""

records = [
    (
        row["item_id"],
        row["store_id"],
        int(row["day_number"]),
        float(row["predicted_sales"])
    )
    for _, row in df.iterrows()
]

try:
    cursor.executemany(sql, records)
    connection.commit()

    print("Multi-store forecast import completed.")
    print("Rows affected:", cursor.rowcount)
    print("Forecast records processed:", len(records))

except mysql.connector.Error as error:
    connection.rollback()
    print("MySQL error:", error)

finally:
    cursor.close()
    connection.close()

print("Import process finished.")