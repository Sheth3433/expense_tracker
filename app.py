import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

st.title("💰 Smart Expense Tracker")

FILE = "expenses.csv"

# Create file if not exists
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Date","Amount","Category","Description"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# -------- Add Expense --------
st.sidebar.header("Add New Expense")

date = st.sidebar.date_input("Date")
amount = st.sidebar.number_input("Amount", min_value=0.0)
category = st.sidebar.selectbox(
    "Category",
    ["Food","Travel","Shopping","Bills","Other"]
)
desc = st.sidebar.text_input("Description")

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame([[date,amount,category,desc]],
                            columns=df.columns)
    df = pd.concat([df,new_data], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Expense Added!")

# -------- Show Data --------
st.subheader("📊 All Expenses")
st.dataframe(df, use_container_width=True)

# -------- Total --------
st.subheader("Total Spending")
st.metric(label="₹ Total", value=int(df["Amount"].sum()))

# -------- Chart --------
st.subheader("Category Wise Spending")

if not df.empty:
    chart_data = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(chart_data, labels=chart_data.index, autopct="%1.1f%%")
    st.pyplot(fig)

# -------- Download --------
st.download_button(
    "Download Expenses CSV",
    df.to_csv(index=False),
    file_name="expenses.csv",
    mime="text/csv"
)
