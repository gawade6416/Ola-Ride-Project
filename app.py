import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# import psycopg2

sns.set_style("whitegrid")

st.set_page_config(page_title="OLA Ride Insights", layout="wide")

# --------------------------------
# Load Data from PostgreSQL
# --------------------------------


# @st.cache_data
# def load_data():

#     conn = psycopg2.connect(
#         host="localhost",
#         database="ola rides project",
#         user="postgres",
#         password="123456",
#         port="5432"
#     )

#     query = "SELECT * FROM ola_bookings"

#     df = pd.read_sql(query, conn)

#     df.columns = df.columns.str.lower().str.replace(" ", "_")

#     return df

@st.cache_data
def load_data():

    df = pd.read_csv("OlaBookings.csv")

    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # st.write(df.columns)
    return df

df = load_data()

# --------------------------------
# Sidebar Navigation
# --------------------------------

page = st.sidebar.radio(
    "Navigation",
    ["Project Details", "SQL Insights Dashboard"]
)

# =================================
# PAGE 1
# =================================

if page == "Project Details":

    st.title("OLA Ride Insights Project")

    st.header("Business Objective")
    
    st.write("""
    The objective of this project is to analyze OLA ride booking data to understand
    ride demand, cancellations, customer behaviour, and revenue patterns.
    The insights help improve operational efficiency and customer satisfaction.
    """)

    st.header("Tools Used")
    st.write("""
    - PostgreSQL (SQL Analysis)
    - Power BI (Visualization)
    - Streamlit (Interactive Dashboard)
    """)

    st.header("Dataset Description")
    st.write("""
    The dataset contains ride booking information including vehicle types,
    ride distance, booking status, payment methods, and customer ratings.
    """)
# =================================
# PAGE 2
# =================================

elif page == "SQL Insights Dashboard":

    st.title("SQL Insights Visualization")

    # ---------------- KPI Row ----------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Rides",
        len(df)
    )

    col2.metric(
        "Successful Rides",
        len(df[df["booking_status"] == "Success"])
    )

    col3.metric(
        "Total Revenue",
        f"₹ {df['booking_value'].sum():,.0f}"
    )

    st.markdown("---")

    # ---------------- Dropdown ----------------

    question = st.selectbox(
        "Select SQL Question",
        [
            "1. Successful Bookings",
            "2. Average Ride Distance per Vehicle Type",
            "3. Cancelled Rides by Customer",
            "4. Top 5 Customers by Number of Rides",
            "5. Driver Cancellations (Personal/Car Issue)",
            "6. Max & Min Driver Ratings (Prime Sedan)",
            "7. Rides Paid Using UPI",
            "8. Average Customer Rating by Vehicle",
            "9. Total Revenue from Successful Rides",
            "10. Incomplete Rides with Reason"
        ]
    )

    queries = {

        "1. Successful Bookings":
        "SELECT * FROM ola_bookings WHERE booking_status='Success';",

        "2. Average Ride Distance per Vehicle Type":
        "SELECT vehicle_type, AVG(ride_distance) FROM ola_bookings GROUP BY vehicle_type;",

        "3. Cancelled Rides by Customer":
        "SELECT COUNT(*) FROM ola_bookings WHERE booking_status='Canceled by Customer';",

        "4. Top 5 Customers by Number of Rides":
        "SELECT customer_id, COUNT(*) FROM ola_bookings GROUP BY customer_id ORDER BY COUNT(*) DESC LIMIT 5;",

        "5. Driver Cancellations (Personal/Car Issue)":
        "SELECT COUNT(*) FROM ola_bookings WHERE canceled_rides_by_driver='Personal & Car related issue';",

        "6. Max & Min Driver Ratings (Prime Sedan)":
        "SELECT MAX(driver_ratings), MIN(driver_ratings) FROM ola_bookings WHERE vehicle_type='Prime Sedan';",

        "7. Rides Paid Using UPI":
        "SELECT * FROM ola_bookings WHERE payment_method='UPI';",

        "8. Average Customer Rating by Vehicle":
        "SELECT vehicle_type, AVG(customer_rating) FROM ola_bookings GROUP BY vehicle_type;",

        "9. Total Revenue from Successful Rides":
        "SELECT SUM(booking_value) FROM ola_bookings WHERE booking_status='Success';",

        "10. Incomplete Rides with Reason":
        "SELECT booking_id, incomplete_rides_reason FROM ola_bookings WHERE incomplete_rides='Yes';"
    }

    # ---------------- SQL Query ----------------

    st.subheader("SQL Query")
    st.code(queries[question], language="sql")

    # ---------------- Query Result ----------------

    st.subheader("Query Result Table")

    result = None

    if question == "1. Successful Bookings":
        result = df[df["booking_status"] == "Success"]

    elif question == "2. Average Ride Distance per Vehicle Type":
        result = df.groupby("vehicle_type")["ride_distance"].mean().reset_index()

    elif question == "3. Cancelled Rides by Customer":
        result = df[df["booking_status"] == "Canceled by Customer"]

    elif question == "4. Top 5 Customers by Number of Rides":
        result = df.groupby("customer_id").size().reset_index(name="total_rides")
        result = result.sort_values("total_rides", ascending=False).head(5)

    elif question == "5. Driver Cancellations (Personal/Car Issue)":
        result = df[df["canceled_rides_by_driver"] == "Personal & Car related issue"]

    elif question == "6. Max & Min Driver Ratings (Prime Sedan)":
        result = df[df["vehicle_type"] == "Prime Sedan"][["driver_ratings"]]

    elif question == "7. Rides Paid Using UPI":
        result = df[df["payment_method"] == "UPI"]

    elif question == "8. Average Customer Rating by Vehicle":
        result = df.groupby("vehicle_type")["customer_rating"].mean().reset_index()

    elif question == "9. Total Revenue from Successful Rides":
        revenue = df[df["booking_status"] == "Success"]["booking_value"].sum()
        result = pd.DataFrame({"total_revenue":[revenue]})

    elif question == "10. Incomplete Rides with Reason":
        result = df[df["incomplete_rides"] == "Yes"][["booking_id","incomplete_rides_reason"]]

    st.dataframe(result)

    st.markdown("---")

    # ---------------- Visualization ----------------

    st.subheader("Visualization")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        # Q1
        if question == "1. Successful Bookings":

            fig, ax = plt.subplots(figsize=(6,4))
            chart = result["vehicle_type"].value_counts()
            chart.plot(kind="bar", ax=ax)

            ax.set_xlabel("Vehicle Type")
            ax.set_ylabel("Number of Rides")

            st.pyplot(fig)

        # Q2 horizontal
        elif question == "2. Average Ride Distance per Vehicle Type":

            fig, ax = plt.subplots(figsize=(6,4))

            sns.barplot(
                data=result,
                y="vehicle_type",
                x="ride_distance",
                ax=ax
            )

            ax.set_xlabel("Average Ride Distance")

            st.pyplot(fig)

        # Q3 pie
        elif question == "3. Cancelled Rides by Customer":

            cancelled = len(result)
            other = len(df) - cancelled
            values = [cancelled, other]

            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                values,
                labels=["Cancelled","Other"],
                autopct=lambda p: f'{int(p*sum(values)/100)}'
            )

            st.pyplot(fig)

        # Q4
        elif question == "4. Top 5 Customers by Number of Rides":

            fig, ax = plt.subplots(figsize=(6,4))

            sns.barplot(
                data=result,
                x="customer_id",
                y="total_rides",
                ax=ax
            )

            st.pyplot(fig)

        # Q5 pie
        elif question == "5. Driver Cancellations (Personal/Car Issue)":

            driver_cancel = len(result)
            other = len(df) - driver_cancel

            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                [driver_cancel, other],
                labels=["Driver Cancellation","Other"],
                autopct=lambda p: f'{int(p*sum([driver_cancel, other])/100)}'
            )

            st.pyplot(fig)

        # Q6 KPI
        elif question == "6. Max & Min Driver Ratings (Prime Sedan)":

            col1, col2 = st.columns(2)

            col1.metric("Max Rating", result["driver_ratings"].max())
            col2.metric("Min Rating", result["driver_ratings"].min())

        # Q7 pie
        elif question == "7. Rides Paid Using UPI":

            counts = df["payment_method"].value_counts()

            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                counts.values,
                labels=counts.index,
                autopct=lambda p: f'{int(p*sum(counts.values)/100)}'
            )

            st.pyplot(fig)

        # Q8 horizontal
        elif question == "8. Average Customer Rating by Vehicle":

            fig, ax = plt.subplots(figsize=(6,4))

            sns.barplot(
                data=result,
                y="vehicle_type",
                x="customer_rating",
                ax=ax
            )

            ax.set_xlabel("Average Rating")

            st.pyplot(fig)

        # Q9 KPI
        elif question == "9. Total Revenue from Successful Rides":

            st.metric(
                "Total Revenue from Successful Rides",
                f"₹ {result['total_revenue'][0]:,.0f}"
            )

        # Q10 pie
        elif question == "10. Incomplete Rides with Reason":

            counts = result["incomplete_rides_reason"].value_counts()

            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                counts.values,
                labels=counts.index,
                autopct=lambda p: f'{int(p*sum(counts.values)/100)}'
            )

            st.pyplot(fig)