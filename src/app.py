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
        weight_df = pd.read_csv(weight_file)
        weight_df["Date"] = pd.to_datetime(weight_df["Date"])
        df = weight_df.sort_values("Date")

        source_unit = st.selectbox("What unit is your weight data in?", options=["kg", "lb"], index=0, key="dashboard_source_unit")
        display_unit = st.selectbox("Display Weight In:", options=["kg", "lb"], index=0, key="dashboard_display_unit")

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

        # === CORRELATION AND ENERGY ANALYSIS ===
        st.subheader("Correlation Analysis: Nutrition vs Weight")

        nutrition_file = "data/nutrition_latest.csv"
        if not os.path.exists(nutrition_file):
            st.warning("No nutrition data found. Please upload it via the Nutrition tab.")
        else:
            nutrition_df = pd.read_csv(nutrition_file)
            nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"])

            daily_nutrition = nutrition_df.groupby("Date").agg({
                "Calories": "sum",
                "Protein (g)": "sum",
                "Carbohydrates (g)": "sum",
                "Fat (g)": "sum"
            }).reset_index()

            merged_df = pd.merge(df[["Date", "Display Weight"]], daily_nutrition, on="Date", how="inner")

            # === Lagged Calorie Correlation ===
            st.markdown("""
            ### Lagged Calorie Correlation
            This section checks how calorie intake from **1–3 days ago** relates to your weight.  
            Correlation ranges from **-1 (inverse)** to **+1 (direct)**.
            """)

            lagged_corr_df = merged_df.copy()
            for lag in [1, 2, 3]:
                lagged_corr_df[f"Calories_lag{lag}"] = lagged_corr_df["Calories"].shift(lag)

            lag_corrs = {
                f"Calories lag {lag} days": lagged_corr_df[[f"Calories_lag{lag}", "Display Weight"]].corr().iloc[0, 1]
                for lag in [1, 2, 3]
            }

            lagged_corrs_df = pd.DataFrame.from_dict(
                lag_corrs, orient="index", columns=["Correlation with Weight"]
            ).rename_axis("Lag").round(3)
            lagged_corrs_df["Units"] = "Unitless (−1 to 1)"
            st.table(lagged_corrs_df)

            # === Calories per kg Gained/Lost ===
            st.markdown("""
            ### Estimated Calories per kg Gained or Lost
            This estimates how many kcal it took for your body to gain/lose 1 kg based on your calorie intake and weight data.
            """)

            start_date = merged_df["Date"].min()
            end_date = merged_df["Date"].max()
            weight_start = merged_df.loc[merged_df["Date"] == start_date, "Display Weight"].values[0]
            weight_end = merged_df.loc[merged_df["Date"] == end_date, "Display Weight"].values[0]
            weight_diff = weight_end - weight_start
            total_days = (end_date - start_date).days + 1
            avg_daily_cal = merged_df["Calories"].mean()

            try:
                estimated_tdee = avg_daily_cal - (weight_diff * 7700 / total_days)
                net_calories = (avg_daily_cal - estimated_tdee) * total_days
                kcal_per_kg = net_calories / weight_diff if weight_diff != 0 else None

                st.metric("Net Weight Change", f"{weight_diff:.2f} kg")
                st.metric("Avg Daily Calories", f"{avg_daily_cal:,.0f} kcal/day")
                st.metric("Estimated TDEE", f"{estimated_tdee:,.0f} kcal/day")

                if kcal_per_kg:
                    st.metric("Calories per kg Gained/Lost", f"{abs(kcal_per_kg):,.0f} kcal/kg")
                else:
                    st.info("No net weight change detected. Cannot estimate kcal per kg.")
            except Exception as e:
                st.error(f"Error in estimation: {e}")

# === NUTRITION TAB ===
with tab2:
    show_nutrition_tab()

# === WEIGHT TAB ===
with tab3:
    show_weight_tab()