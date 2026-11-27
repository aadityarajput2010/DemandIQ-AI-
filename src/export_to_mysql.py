import mysql.connector
from getpass import getpass

def create_connection():
    password = input("Enter your MySQL root password: ")

    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=password,
        database="demandiq"
    )

try:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")

    print("\nTables in DemandIQ database:")

    for table in cursor.fetchall():
        print(table[0])

    cursor.close()
    connection.close()

    print("\nDatabase verification successful!")

except mysql.connector.Error as error:
    print("Error:", error)