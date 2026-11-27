import mysql.connector
from getpass import getpass

password = input("Enter your MySQL root password: ")

try:
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=password,
        database="demandiq"
    )

    print("Successfully connected to DemandIQ AI database!")

    connection.close()

except mysql.connector.Error as error:
    print("MySQL connection failed:", error)