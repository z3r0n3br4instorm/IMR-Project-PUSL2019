import streamlit as st
import pandas as pd
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import numpy.core.multiarray
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from collections import Counter
import datetime as dt
from SystemFiles.DatabaseEngine import SystemDB
import av
import random

class Interface:
    def __init__(self):
        self.placeholder = st.empty()
        self.db = SystemDB('54.169.119.236', 'POS', 'sa', '0_v1ru51234')
        self.notLoggedIn = True
        self.resetBar = False
        # Check if the genRandomNo in the database
        with st.spinner("Generating a Customer ID for You..."):
            if 'customerID' not in st.session_state:
                while True:
                    genRandomNo = random.randint(100000,1000000)
                    query = f"SELECT CustomerID FROM Customer WHERE CustomerID = {genRandomNo}"
                    if self.db.cursor(query) == []:
                        st.session_state.customerID = genRandomNo
                        break
                    else:
                        pass
        if 'cart' not in st.session_state:
            st.session_state.cart = []

    def adminInterface(self):
        # Add spinning cogwheel emoji using HTML and CSS
        if st.session_state.customerID != 0:
            st.toast("Not logged in as admin !")
            self.adminLogin()
            return "Error"
        else:
            st.toast("Welcome Back System Administrator !")
        st.markdown("""
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .spinning-emoji {
                display: inline-block;
                animation: spin 2s linear infinite;
            }
            </style>
            <h1>// Admin Dashboard <span class="spinning-emoji">⚙️</span></h1>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Database Tables:")
        # Show All Tables inside a markdown table
        tables = self.db.cursor("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        st.table(tables)
        st.markdown("---")
        st.subheader("MSSQL Admin Shell:")
        query = st.text_area("Enter your SQL query here:")
        if st.button("Execute"):
            with st.spinner("Executing query..."):
                try:
                    result = self.db.cursor(query)
                    st.write(result)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        st.markdown("---")
        st.subheader("Admin Functions:")
        if st.button("Create Tables"):
            with st.spinner("Creating tables..."):
                self.db.adminFunctionsCreateTables()
                st.success("Tables created successfully!")
        if st.button("Insert Products from CSV"):
            with st.spinner("Inserting products..."):
                self.db.insertProductsFromCSV("dataset.csv")
                st.success("Products inserted successfully!")
        st.markdown("---")
        st.subheader("Default Camera Device Selection:")
        st.write("Select the default camera device for the barcode scanner:")
        camera_device = st.selectbox("Camera Device", range(10))
        st.write(f"Selected Camera Device: {camera_device}")
        st.markdown("---")


    def login(self):
        with self.placeholder.container():
            st.title("Enter Your Data to Register to our system and get Discounts, Promotions and various other benifits...")
            uname = st.text_input("Your Name", key="name")
            email = st.text_input("Your Email", key="email")
            pno = st.text_input("Your Phone Number", key="phone")
            print(uname, email, pno)
            if (uname == "" or email == "" or pno == ""):
                st.warning("Please fill in all the fields to continue...")
            else:
                if st.button("Save User"):
                    if self.db.cursor(f"""SELECT * FROM Customer_Contact WHERE C_Contact = '{str(pno)}'""") == []:
                        query = f"""INSERT INTO Customer (CustomerID, C_Name, C_Email) VALUES ({st.session_state.customerID}, '{str(uname)}', '{str(email)}');"""
                        query2 = f"""INSERT INTO Customer_Contact (CustomerID, C_Contact) VALUES ({st.session_state.customerID}, '{str(pno)}');"""
                        self.db.cursor(query)
                        self.db.cursor(query2)
                        st.success("User Saved!")
                        st.query_params.update({"page": "main"})
                        # Refresh
                        self.mainScreen()
                    else:
                        st.error("User Already Exists !")

    def adminLogin(self):
        with self.placeholder.container():
            st.title("Admin Login")
            uname = st.text_input("Username", key="admin_name")
            pword = st.text_input("Password", type="password", key="admin_password")
            if (uname == "" or pword == ""):
                st.warning("Please fill in all the fields to continue...")
            else:
                if st.button("Login"):
                    # print(self.db.cursor(f"SELECT * FROM AdminUsers WHERE Username = '{uname}'"), uname, pword)
                    data =  self.db.cursor(f"SELECT * FROM AdminUsers WHERE Username = '{uname}'")
                    if uname == data[0][1] and pword == data[0][2]:
                        st.session_state.customerID = 0
                        st.query_params.update({"page": "admin"})
                        self.adminInterface()
                    else:
                        st.error("Invalid credentials. Please try again.")

    def searchAndBuy(self):
        with self.placeholder.container():
            st.title("Search and Buy")
            pay = st.button(
                f"Proceed to Pay ->"
                # key=f"button_pay",
                # help=f"Redirect to payment page"
            )
            dataSet = self.db.cursor("SELECT P_Name, P_Qty, Price, ProductID FROM Product")
            search = st.text_input("Search for products", key="search")

            if search:
                with st.spinner("Searching..."):
                    rows = dataSet
                    found = False
                    for row in rows:
                        if search.lower() in row[0].lower():
                            found = True
                            availability = "Available" if row[1] > 0 else "Not Available"
                            with st.container():
                                st.markdown(
                                    f"""
                                    <div style='border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px;'>
                                        <b>Product:</b> {row[0]}<br>
                                        <b>Price:</b> {row[2]}<br>
                                        <b>Availability:</b> {availability}<br>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                clicked = st.button(
                                    f"Add to Cart",
                                    key=f"button_{row[0]}",
                                    help=f"Click to select {row[0]}"
                                )
                                if clicked:
                                    with st.spinner("Adding to cart..."):
                                        st.session_state.cart.append(row[3])  # Add product ID to cart
                                        st.success("Added To Cart")

                                        # Ensure that the cart display gets updated after adding
                                        st.info(f"🛒 {len(st.session_state.cart)}")
                                if pay:
                                    st.info("Press again to confirm...")
                                    st.query_params.update({"page": "paymentProcessor"})
                    if not found:
                        st.info("No matching products found.")
            else:
                st.warning("Please enter a product name to search.")

    def displayBarChart(self, inventory):
        # Get inventory data from database
        data = {
            "Category": [],
            "Values": []
        }
        rows = inventory
        for row in rows:
            data["Category"].append(row[0])
            data["Values"].append(row[1])

        df = pd.DataFrame(data)
        if not df.empty:
            st.bar_chart(df.set_index("Category"))

    def mainScreen(self):
        with self.placeholder.container():
            self.resetBar = True
            st.title("Frenzy Mart Self Checkout System")
            st.toast("DO NOT REFRESH THE PAGE UNTIL YOU ARE DONE SHOPPING !")
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 2, 1, 1,1])
            with col1:
                if st.button("⚙️ Admin"):  # Bar chart emoji
                    with st.spinner("Initializing Interface ..."):
                        st.query_params.update({"page": "admin"})
                        st.rerun()
            with col3:
                st.empty()
            with col4:
                if st.button("Manual ->"):
                    with st.spinner("Initializing Interface..."):
                        st.query_params.update({"page": "searchAndBuy"})
                        st.rerun()
            with col5:
                if st.button("Automatic 𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃"):
                    st.toast("This functionality is available only in a local system !")
                    with st.spinner("Initializing Interface..."):
                        st.query_params.update({"page": "barcodeScanner"})
                        st.rerun()
            with col6:
                if st.button("💸 Pay"):
                    with st.spinner("Initializing Interface..."):
                        st.query_params.update({"page": "paymentProcessor"})
                        st.rerun()

            with st.spinner("Waiting for Database..."):
                st.subheader("Inventory Status")
                inventory = self.db.cursor("SELECT P_Name, P_Qty FROM Product")
                self.displayBarChart(inventory)

            st.subheader(f"🛒 {len(st.session_state.cart)}")
            st.subheader(F"🔑 {st.session_state.customerID}")


    def barCodeScanner(self):
        st.title("Barcode Scanner")
        # Open the webcam
        cap = cv2.VideoCapture(1)
        # Display the video feed in Streamlit
        stframe = st.empty()
        persistance = 0
        with st.spinner("Detecting barcodes..."):
            # if st.button("Proceed to pay"):
            #     with st.spinner("Initializing Interface..."):
            #         st.query_params.update({"page": "paymentProcessor"})
            try:
                while True:
                    ret, frame = cap.read()

                    if not ret:
                        st.error("Failed to capture image from webcam.")
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    barcodes = decode(gray)
                    for barcode in barcodes:
                        rect_points = barcode.polygon
                        if len(rect_points) == 4:
                            pts = np.array(rect_points, dtype=np.int32)
                            pts = pts.reshape((-1, 1, 2))
                            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                        else:
                            rect = barcode.rect
                            cv2.rectangle(frame, (rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height), (0, 255, 0), 2)

                        barcode_data = barcode.data.decode('utf-8')
                        if persistance != barcode_data:
                            st.toast(f"New Barcode: {barcode_data} Detected !")
                            persistance = barcode_data
                            st.toast("\b Added to cart !")
                            st.info("Item Added to cart...")
                            st.session_state.cart.append(int(barcode_data.replace('0', '')))
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    stframe.image(frame_rgb)
            except:
                st.error("Failed to capture image from webcam. Retry...")

        # Release the webcam
        cap.release()

    def paymentProcessor(self):
        st.title("Payment Processor 💸")
        totalPrice = 0
        with st.spinner("Communicating with database..."):
            cart_items = st.session_state.cart
            if not cart_items:
                st.error("Your cart is empty!")
                return

            item_ids = ', '.join(map(str, cart_items))
            item_qty = Counter(st.session_state.cart)
            query = f"""
            SELECT P_Name,Price, ProductID
            FROM Product
            WHERE ProductID IN ({item_ids})
            """

            # Execute the query
            results = self.db.cursor(query)
            # Display results
            st.subheader("Your cart items:")
            print(item_qty)
            for row in results:
                st.info(f"Item: {row[0]}, Price: {row[1]}, Quantity: {item_qty[row[2]]}")
            for key, value in item_qty.items():
                for row in results:
                    if key == row[2]:
                        totalPrice += row[1] * value
            st.subheader(f"Total Price : ${totalPrice}")
            st.title("Enter Your Phone Number to continue...")
            pNO = st.text_input("Phone Number (No Country Code):")
            if st.button("Pay"):
                with st.spinner("Processing Payment..."):
                    try:
                        if self.db.cursor(f"SELECT * FROM Customer_Contact WHERE C_Contact = {pNO}") == []:
                            # Add customer first
                            addToCustomer = f"""INSERT INTO Customer (CustomerID, C_Name, C_Email) VALUES ({st.session_state.customerID}, 'GuestUser', 'GuestUser@gu.com');"""
                            addToInvoice = f"""
                                INSERT INTO Invoice (InvoiceID, Inv_Date, Total_Amount, CustomerID)
                                VALUES (
                                    (SELECT ISNULL(MAX(InvoiceID), 0) + 1 FROM Invoice),
                                    GETDATE(),
                                    {float(totalPrice)},
                                    {st.session_state.customerID}
                                );
                            """
                            # Execute the invoice insert (assuming you execute this query correctly here)
                            # check if user's phone number exists in the database
                            self.db.cursor(addToCustomer)
                            st.success(f"Customer Added !")
                            self.db.cursor(addToInvoice)
                            st.success(f"Payment Successful !")
                            st.session_state.cart.clear()
                            with st.spinner("Initializing Interface..."):
                                st.query_params.update({"page": "login"})
                                self.login()
                        else :
                            # add the data to proper invoice
                            # Get customerID
                            query = f"SELECT CustomerID FROM Customer_Contact WHERE C_Contact = {pNO}"
                            getNewId = self.db.cursor(query)
                            getCName = self.db.cursor(f"SELECT C_Name FROM Customer WHERE CustomerID = {getNewId[0][0]}")
                            st.session_state.customerID = getNewId[0][0]
                            addToInvoice = f"""
                                INSERT INTO Invoice (InvoiceID, Inv_Date, Total_Amount, CustomerID)
                                VALUES (
                                    (SELECT ISNULL(MAX(InvoiceID), 0) + 1 FROM Invoice),
                                    GETDATE(),
                                    {float(totalPrice)},
                                    {st.session_state.customerID}
                                );
                            """
                            self.db.cursor(addToInvoice)
                            st.success(f"Payment Successful !, Thank you for shopping with us Mr. {getCName[0][0]}")
                            st.session_state.cart.clear()
                            with st.spinner("Initializing Interface..."):
                                st.query_params.update({"page": "main"})
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            if (st.button("Done")):
                st.info("Press again to confirm...")
                with st.spinner("Initializing Interface..."):
                    st.query_params.update({"page": "main"})


    def route(self):
        params = st.query_params
        page = params.get("page", "main")

        if page == "main":
            self.mainScreen()
        elif page == "searchAndBuy":
            self.searchAndBuy()
        elif page == "barcodeScanner":
            self.barCodeScanner()
        elif page == "paymentProcessor":
            self.paymentProcessor()
        elif page == "admin":
            self.adminInterface()
        elif page == "login":
            self.login()
        else:
            st.error("Page not found!")

if __name__ == "__main__":
    interface = Interface()
    interface.route()
