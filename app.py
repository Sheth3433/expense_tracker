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

# -------- Show Data with Edit/Delete --------
st.subheader("📊 All Expenses")

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

for index, row in df.iterrows():

    col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,3,1,1])

    col1.write(row["Date"])
    col2.write(row["Amount"])
    col3.write(row["Category"])
    col4.write(row["Description"])

    # Edit Button
    if col5.button("Edit", key=f"edit{index}"):
        st.session_state.edit_index = index

    # Delete Button
    if col6.button("Delete", key=f"delete{index}"):
        df = df.drop(index)
        df.to_csv(FILE, index=False)
        st.rerun()


# -------- Edit Form --------
if st.session_state.edit_index is not None:

    st.subheader("✏️ Edit Expense")

    i = st.session_state.edit_index

    edit_date = st.date_input("Date", pd.to_datetime(df.loc[i, "Date"]))
    edit_amount = st.number_input("Amount", value=float(df.loc[i, "Amount"]))
    edit_category = st.selectbox(
        "Category",
        ["Food","Travel","Shopping","Bills","Other"],
        index=["Food","Travel","Shopping","Bills","Other"].index(df.loc[i, "Category"])
    )
    edit_desc = st.text_input("Description", df.loc[i, "Description"])

    col1, col2 = st.columns(2)

    if col1.button("Update Expense"):
        df.loc[i] = [edit_date, edit_amount, edit_category, edit_desc]
        df.to_csv(FILE, index=False)
        st.session_state.edit_index = None
        st.success("Updated Successfully!")
        st.rerun()

    if col2.button("Cancel"):
        st.session_state.edit_index = None
        st.rerun()
# -------- Download --------
st.download_button(
    "Download Expenses CSV",
    df.to_csv(index=False),
    file_name="expenses.csv",
    mime="text/csv"
)
