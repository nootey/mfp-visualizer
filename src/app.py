import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

from nutrition import show_nutrition_tab
from weight import show_weight_tab
from utils import download_figure

st.set_page_config(page_title="MyFitnessPal Visualizer", layout="wide")
st.title("MyFitnessPal Data Visualizer")

# Session Reset
if st.sidebar.button("Clear Stored Data"):
    st.session_state.clear()
    st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "Nutrition Summary", "Weight Tracking"])

# === DASHBOARD OVERVIEW ===
with tab1:
    st.header("Weight Trend Overview")

    weight_file = "data/weight_latest.csv"
    if not os.path.exists(weight_file):
        st.warning("No weight data found. Please upload from the Weight tab first.")
    else:
        df = pd.read_csv(weight_file)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Allow user to specify source and display units
        source_unit = st.selectbox("What unit is your weight data in?", options=["kg", "lb"], index=0, key="dashboard_source_unit")
        display_unit = st.selectbox("Display Weight In:", options=["kg", "lb"], index=0, key="dashboard_display_unit")

        # Apply conversion logic
        if source_unit == display_unit:
            df["Display Weight"] = df["Weight"]
        elif source_unit == "lb" and display_unit == "kg":
            df["Display Weight"] = df["Weight"] * 0.453592
        elif source_unit == "kg" and display_unit == "lb":
            df["Display Weight"] = df["Weight"] / 0.453592

        def plot_trend(data, label):
            if len(data) < 2:
                st.info(f"Not enough data to analyze trend for {label}.")
                return
            data = data.copy()
            data["DayIndex"] = (data["Date"] - data["Date"].min()).dt.days
            X = data["DayIndex"].values.reshape(-1, 1)
            y = data["Display Weight"].values
            model = LinearRegression().fit(X, y)
            data["Trend"] = model.predict(X)
            slope = model.coef_[0]
            trend = "Upward" if slope > 0 else "Downward" if slope < 0 else "Flat"

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.lineplot(data=data, x="Date", y="Display Weight", ax=ax, label="Weight")
            sns.lineplot(data=data, x="Date", y="Trend", ax=ax, label="Trend", linestyle='--')
            ax.set_title(f"Weight Trend – {label} ({trend})")
            ax.set_ylabel(f"Weight ({display_unit})")
            ax.set_xlabel("Date")
            st.pyplot(fig)

        today = pd.Timestamp.today()
        df_month = df[df["Date"].dt.to_period("M") == today.to_period("M")]
        df_year = df[df["Date"].dt.year == today.year]

        st.subheader("This Month")
        plot_trend(df_month, "This Month")

        st.subheader("This Year")
        plot_trend(df_year, "This Year")

        st.subheader("All Time")
        plot_trend(df, "All Time")

# === NUTRITION TAB ===
with tab2:
    show_nutrition_tab()

# === WEIGHT TAB ===
with tab3:
    show_weight_tab()