from DatabaseEngine import SystemDB
import random
db = SystemDB('54.169.119.236', 'POS', 'sa', '0_v1ru51234')

while True:
    while True:
    query = f"SELECT CustomerID FROM Customer WHERE CustomerID = {genRandomNo}"
    if db.cursor(query).fetchall() == []:
        break
    else:
        print(db.cursor(query).fetchall())
