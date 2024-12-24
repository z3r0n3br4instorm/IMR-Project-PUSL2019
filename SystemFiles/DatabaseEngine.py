import pyodbc
import csv
from posix import close
import threading
import time

class SystemDB:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        refreshStockThread = threading.Thread(target=self.refreshStock)
        refreshStockThread.start()

    def estConn(self):
        # Connection string
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        try:
            # Connect to SQL Server
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            print(f"Error: {e}")
            return None

    def cursor(self,query):
        conn = self.estConn()
        cursor = conn.cursor()
        exec = cursor.execute(query)
        try:
            result = exec.fetchall()
        except:
            result = "Success"
        conn.commit()
        conn.close()
        return result

    def refreshStock(self):
        if True:
            print("Refreshing Stock...")
            try:
                query = f"""
                UPDATE Stock
                SET St_Qty = (
                    SELECT SUM(P_Qty)
                    FROM Product
                )
                WHERE StockID = 1; -- Adjust the StockID or condition as needed
                """
                result = self.cursor(query)
                print(result)
            except Exception as e:
                print(f"Error: {e}")

    def adminFunctionsUpdateInventory(self, product_id, qty, supplierID):
        query = f"""UPDATE Product SET P_Qty = P_Qty + {qty} WHERE ProductID = {product_id};"""
        query2 = f"""UPDATE Supplier SET Sup_Qty = Sup_Qty + {qty} WHERE SupplierID = {supplierID};"""
        result = self.cursor(query)
        result2 = self.cursor(query2)
        print(result, result2)
        return result

    def adminFunctionsCreateTables(self):
        queries = [
            # Customer table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Customer' AND xtype='U')
            BEGIN
                CREATE TABLE Customer (
                    CustomerID INT PRIMARY KEY,
                    C_Name VARCHAR(255) NOT NULL,
                    C_Email VARCHAR(255) NOT NULL
                );
            END;""",

            # Customer_Contact table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Customer_Contact' AND xtype='U')
            BEGIN
                CREATE TABLE Customer_Contact (
                    CustomerID INT PRIMARY KEY,
                    C_Contact VARCHAR(20) NOT NULL,
                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
                );
            END;""",

            # Product table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Product' AND xtype='U')
            BEGIN
                CREATE TABLE Product (
                    ProductID INT PRIMARY KEY,
                    P_Name VARCHAR(255) NOT NULL,
                    Price FLOAT NOT NULL,
                    P_Qty INT NOT NULL
                );
            END;""",

            # Supplier table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Supplier' AND xtype='U')
            BEGIN
                CREATE TABLE Supplier (
                    SupplierID INT PRIMARY KEY,
                    Sup_Name VARCHAR(255) NOT NULL,
                    Sup_Email VARCHAR(255) NOT NULL,
                    Sup_Qty INT NOT NULL
                );
            END;""",

            # Supplier_Contact table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Supplier_Contact' AND xtype='U')
            BEGIN
                CREATE TABLE Supplier_Contact (
                    SupplierID INT PRIMARY KEY,
                    Sup_Contact VARCHAR(20) NOT NULL,
                    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
                );
            END;""",

            # Sales table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Sales' AND xtype='U')
            BEGIN
                CREATE TABLE Sales (
                    SalesID INT IDENTITY(1,1) PRIMARY KEY,  -- Auto-generates the SalesID starting from 1
                    S_Date DATETIME NOT NULL,
                    TotalSales FLOAT NOT NULL,
                    ReportID INT NOT NULL
                );
            END;""",

            # Invoice table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Invoice' AND xtype='U')
            BEGIN
                CREATE TABLE Invoice (
                    InvoiceID INT PRIMARY KEY,
                    Inv_Date DATETIME NOT NULL,
                    Total_Amount FLOAT NOT NULL,
                    CustomerID INT NOT NULL,
                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
                );
            END;""",

            # Stock table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Stock' AND xtype='U')
            BEGIN
                CREATE TABLE Stock (
                    StockID INT PRIMARY KEY,
                    St_Qty INT NOT NULL
                );
            END;""",

            # Discount table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Discount' AND xtype='U')
            BEGIN
                CREATE TABLE Discount (
                    DiscountID INT PRIMARY KEY,
                    Percentage FLOAT NOT NULL
                );
            END;""",

            # Sales_Report table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Sales_Report' AND xtype='U')
            BEGIN
                CREATE TABLE Sales_Report (
                    S_ReportID INT PRIMARY KEY,
                    SR_Date DATETIME NOT NULL,
                    SR_Description VARCHAR(255) NOT NULL
                );
            END;""",

            # Inventory_Report table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Inventory_Report' AND xtype='U')
            BEGIN
                CREATE TABLE Inventory_Report (
                    In_ReportID INT PRIMARY KEY,
                    In_Date DATETIME NOT NULL,
                    In_Description VARCHAR(255) NOT NULL
                );
            END;""",

            # Supplier_Stock table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Supplier_Stock' AND xtype='U')
            BEGIN
                CREATE TABLE Supplier_Stock (
                    SupplierID INT PRIMARY KEY,
                    StockID INT NOT NULL,
                    Sup_Qty INT NOT NULL,
                    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID),
                    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
                );
            END;""",

            # Sales_Report_Products table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Sales_Report_Products' AND xtype='U')
            BEGIN
                CREATE TABLE Sales_Report_Products (
                    SalesID INT PRIMARY KEY,
                    ProductID INT NOT NULL,
                    FOREIGN KEY (SalesID) REFERENCES Sales(SalesID),
                    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
                );
            END;""",

            # Sales_Quantity table
            """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Sales_Quantity' AND xtype='U')
            BEGIN
                CREATE TABLE Sales_Quantity (
                    SalesID INT PRIMARY KEY,
                    P_Qty INT NOT NULL,
                    FOREIGN KEY (SalesID) REFERENCES Sales(SalesID)
                );
            END;"""
        ]
        conn = self.estConn()
        if conn:
            cursor = conn.cursor()
            for query in queries:
                try:
                    cursor.execute(query)
                    print("Table creation executed successfully.")
                except Exception as e:
                    print(f"Error creating table: {e}")
            conn.commit()
            conn.close()

    def insertProductsFromCSV(self, csv_file):
            conn = self.estConn()
            if conn:
                cursor = conn.cursor()

                try:
                    # Open the CSV file and read the data
                    with open(csv_file, newline='') as file:
                        csv_reader = csv.DictReader(file)

                        # Loop through each row in the CSV and insert data into the Product table
                        for row in csv_reader:
                            product_id = int(row['ProductID'])
                            product_name = row['P_Name']
                            price = float(row['Price'])
                            qty = int(row['P_Qty'])

                            # SQL query to insert data into Product table
                            query = """INSERT INTO Product (ProductID, P_Name, Price, P_Qty)
                                    VALUES (?, ?, ?, ?)"""
                            cursor.execute(query, (product_id, product_name, price, qty))

                        # Commit the transaction
                        conn.commit()
                        print("100 products inserted successfully from CSV file.")

                except Exception as e:
                    print(f"Error inserting products: {e}")

                finally:
                    conn.close()



if __name__ == "__main__":
    server = '54.169.119.236'
    database = 'POS'
    username = 'sa'
    password = '0_v1ru51234'
    dataIn = input("Enter 'y' to create tables: ")
    if dataIn == "y":
        SystemDB(server, database, username, password).adminFunctionsCreateTables()
    dataIn = input("Enter 'y' to insert products from CSV: ")
    if dataIn == "y":
        SystemDB(server, database, username, password).insertProductsFromCSV('dataset.csv')
