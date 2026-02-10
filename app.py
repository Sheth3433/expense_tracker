import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="SmartSpend AI", layout="wide")

st.title("💰 SmartSpend AI — Predictive Finance Dashboard")

FILE = "expenses.csv"

# Create CSV if not exists
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Date","Amount","Category","Description"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)


# ================= AUTO CATEGORY =================
def auto_category(desc):
    desc = desc.lower()

    if any(word in desc for word in ["uber","ola","rapido","metro"]):
        return "Travel"
    elif any(word in desc for word in ["pizza","burger","restaurant","cafe","zomato","swiggy"]):
        return "Food"
    elif any(word in desc for word in ["amazon","flipkart","mall","shopping"]):
        return "Shopping"
    elif any(word in desc for word in ["electric","bill","recharge","wifi"]):
        return "Bills"
    else:
        return "Other"


# ================= SIDEBAR =================
st.sidebar.header("➕ Add Expense")

date = st.sidebar.date_input("Date")
amount = st.sidebar.number_input("Amount", min_value=0.0)
desc = st.sidebar.text_input("Description")

category = auto_category(desc) if desc else "Other"
st.sidebar.write(f"📌 Suggested Category: **{category}**")

if st.sidebar.button("Add Expense"):

    new_data = pd.DataFrame([[date,amount,category,desc]],
                            columns=df.columns)

    df = pd.concat([df,new_data], ignore_index=True)
    df.to_csv(FILE, index=False)

    st.sidebar.success("Expense Added!")
    st.rerun()


# ================= TOTAL =================
st.subheader("💵 Total Spending")

total = df["Amount"].sum()
st.metric("Total खर्चा", f"₹ {int(total)}")


# ================= BUDGET =================
st.subheader("🎯 Budget Alert")

budget = st.number_input("Set Monthly Budget", value=10000)

if total > budget:
    st.error("⚠️ Budget exceeded! Control your spending.")
else:
    st.success(f"✅ You are within budget. Remaining ₹ {int(budget-total)}")


# ================= EDIT / DELETE =================

st.subheader("📊 All Expenses")

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

for index, row in df.iterrows():

    col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,3,1,1])

    col1.write(row["Date"])
    col2.write(row["Amount"])
    col3.write(row["Category"])
    col4.write(row["Description"])

    if col5.button("Edit", key=f"edit{index}"):
        st.session_state.edit_index = index

    if col6.button("Delete", key=f"delete{index}"):
        df = df.drop(index)
        df.to_csv(FILE, index=False)
        st.rerun()


# ================= EDIT FORM =================

if st.session_state.edit_index is not None:

    st.subheader("✏️ Edit Expense")

    i = st.session_state.edit_index

    edit_date = st.date_input("Date", pd.to_datetime(df.loc[i, "Date"]))
    edit_amount = st.number_input("Amount", value=float(df.loc[i, "Amount"]))
    edit_desc = st.text_input("Description", df.loc[i, "Description"])

    edit_category = auto_category(edit_desc)

    col1, col2 = st.columns(2)

    if col1.button("Update"):
        df.loc[i] = [edit_date, edit_amount, edit_category, edit_desc]
        df.to_csv(FILE, index=False)
        st.session_state.edit_index = None
        st.success("Updated!")
        st.rerun()

    if col2.button("Cancel"):
        st.session_state.edit_index = None
        st.rerun()


# ================= CHART =================

if not df.empty:

    st.subheader("📈 Category Wise Spending")

    chart_data = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(chart_data, labels=chart_data.index, autopct="%1.1f%%")
    st.pyplot(fig)


# ================= SMART INSIGHTS =================

st.subheader("🧠 Smart Insights")

if len(df) > 5:

    avg = df["Amount"].mean()
    highest = df["Amount"].max()

    st.write(f"👉 Average expense: ₹ {int(avg)}")
    st.write(f"👉 Highest single expense: ₹ {int(highest)}")

    if highest > avg * 2:
        st.warning("⚠️ Unusual large expense detected!")


# ================= PREDICTION =================

st.subheader("🔮 Spending Prediction")

if len(df) > 10:

    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day

    X = df[['Day']]
    y = df['Amount']

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict([[30]])[0]

    st.success(f"📊 Estimated end-of-month spending: ₹ {int(prediction)}")

    avg_daily = df["Amount"].mean()

    if avg_daily > 0:
        days_left = int((budget-total) / avg_daily)

        if days_left > 0:
            st.write(f"💀 At current spending, your money may last **{days_left} days**.")
        else:
            st.error("You are statistically broke.")


# ================= DOWNLOAD =================

st.download_button(
    "Download Expenses CSV",
    df.to_csv(index=False),
    file_name="expenses.csv",
    mime="text/csv"
)
