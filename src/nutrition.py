import os

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import download_figure, filter_date_range

def show_nutrition_tab():
    st.header("Nutrition Summary")

    uploaded_file = st.file_uploader("Upload your Nutrition CSV", type=["csv"], key="nutrition_upload")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/nutrition_latest.csv", index=False)
        st.session_state["nutrition_df_raw"] = df
        st.success("File uploaded and saved.")
    elif os.path.exists("data/nutrition_latest.csv"):
        df = pd.read_csv("data/nutrition_latest.csv")
        st.session_state["nutrition_df_raw"] = df
        st.info("Using previously saved nutrition data.")
    else:
        st.warning("Please upload a Nutrition CSV file to begin.")

    df_raw = st.session_state.get("nutrition_df_raw")
    if df_raw is None:
        st.info("Please upload a Nutrition CSV file to begin.")
        return

    df_raw["Date"] = pd.to_datetime(df_raw["Date"])
    df_raw = df_raw.dropna(subset=["Date", "Calories"])
    df_daily = df_raw.groupby("Date").sum(numeric_only=True).reset_index()
    df_daily = filter_date_range(df_daily, key_prefix="nutrition")

    if df_daily.empty:
        st.warning("No data in selected date range.")
        return

    st.subheader("Daily Calorie Intake")
    st.caption("Total daily calorie intake over the selected time period.")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=df_daily, x="Date", y="Calories", ax=ax1)
    ax1.set_ylabel("Calories")
    ax1.set_xlabel("Date")
    st.pyplot(fig1)
    download_figure(fig1, "calories_over_time.png")

    st.subheader("Nutrition Summary")
    avg_cal = df_daily["Calories"].mean()
    avg_protein = df_daily["Protein (g)"].mean()
    avg_fat = df_daily["Fat (g)"].mean()
    avg_carbs = df_daily["Carbohydrates (g)"].mean()
    max_day = df_daily.loc[df_daily["Calories"].idxmax()]
    min_day = df_daily.loc[df_daily["Calories"].idxmin()]
    st.markdown(f"""
    - **Days Logged:** {df_daily['Date'].nunique()}
    - **Average Calories:** {avg_cal:.0f} kcal
    - **Average Protein:** {avg_protein:.1f} g
    - **Average Fat:** {avg_fat:.1f} g
    - **Average Carbs:** {avg_carbs:.1f} g
    - **Highest Calorie Day:** {max_day['Date'].date()} – {max_day['Calories']} kcal
    - **Lowest Calorie Day:** {min_day['Date'].date()} – {min_day['Calories']} kcal
    """)

    st.subheader("Logging Streaks and Coverage")
    all_dates = pd.date_range(df_daily["Date"].min(), df_daily["Date"].max())
    gaps = all_dates.difference(df_daily["Date"])
    total_days = len(all_dates)
    tracked_days = len(all_dates) - len(gaps)
    coverage = 100 * tracked_days / total_days
    streaks = (df_daily["Date"].diff().dt.days != 1).cumsum()
    longest_streak = df_daily.groupby(streaks).size().max()
    st.markdown(f"""
    - **Longest Logging Streak:** {longest_streak} days
    - **Days Tracked:** {tracked_days}
    - **Total Days in Range:** {total_days}
    - **Tracking Coverage:** {coverage:.1f}%
    """)

    st.subheader("Largest Daily Calorie Change")
    df_daily["Delta"] = df_daily["Calories"].diff()
    valid_indices = []
    for i, row in df_daily.iterrows():
        win = df_daily[(df_daily["Date"] >= row["Date"] - pd.Timedelta(days=7)) &
                       (df_daily["Date"] <= row["Date"] + pd.Timedelta(days=7))]
        if len(win) >= 3:
            valid_indices.append(i)
    if valid_indices:
        valid_delta = df_daily.loc[valid_indices]
        max_valid_idx = valid_delta["Delta"].abs().idxmax()
        max_valid_row = df_daily.loc[max_valid_idx]
        st.markdown(f"- **Most Meaningful Change:** {max_valid_row['Delta']:+.0f} kcal on {max_valid_row['Date'].date()}")
    else:
        st.warning("Not enough data in dense 2-week windows to calculate a meaningful max change.")
    full_max_idx = df_daily["Delta"].abs().idxmax()
    full_max_row = df_daily.loc[full_max_idx]
    st.markdown(f"- **Largest Change (all-time):** {full_max_row['Delta']:+.0f} kcal on {full_max_row['Date'].date()}")

    st.subheader("Average Calories by Weekday")
    df_daily["Weekday"] = df_daily["Date"].dt.day_name()
    weekday_avg = df_daily.groupby("Weekday")["Calories"].mean()
    weekday_avg = weekday_avg.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.barplot(x=weekday_avg.index, y=weekday_avg.values, ax=ax2)
    ax2.set_title("Average Calories by Weekday")
    ax2.set_ylabel("Calories")
    ax2.set_xlabel("Day of Week")
    st.pyplot(fig2)
    download_figure(fig2, "weekday_calories.png")

    st.subheader("Monthly Summary")
    df_daily["Month"] = df_daily["Date"].dt.to_period("M")
    monthly_stats = df_daily.groupby("Month")[["Calories", "Protein (g)", "Fat (g)", "Carbohydrates (g)"]].mean().round(1)
    st.dataframe(monthly_stats)

    st.subheader("Rolling Average and Weekly Calories")
    df_daily["Week"] = df_daily["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_avg = df_daily.groupby("Week")["Calories"].mean().reset_index(name="Weekly Avg")
    df_daily["7d Rolling Avg"] = df_daily["Calories"].rolling(window=7).mean()
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=df_daily, x="Date", y="Calories", label="Daily", ax=ax3)
    sns.lineplot(data=df_daily, x="Date", y="7d Rolling Avg", label="7-Day Avg", ax=ax3)
    sns.lineplot(data=weekly_avg, x="Week", y="Weekly Avg", label="Weekly Avg", linestyle='--', ax=ax3)
    ax3.set_title("Calorie Intake Trends")
    ax3.set_ylabel("Calories")
    ax3.set_xlabel("Date")
    ax3.legend()
    st.pyplot(fig3)
    download_figure(fig3, "calorie_trends.png")

    st.subheader("Nutrient Volatility")
    st.caption("How much your daily intake fluctuates.")
    st.markdown(f"""
    - **Calories Std Dev:** {df_daily["Calories"].std():.0f}
    - **Protein Std Dev:** {df_daily["Protein (g)"].std():.1f} g
    - **Fat Std Dev:** {df_daily["Fat (g)"].std():.1f} g
    - **Carbs Std Dev:** {df_daily["Carbohydrates (g)"].std():.1f} g
    """)

    st.subheader("Macro Ratio Trends")
    st.caption("How your macro balance (protein, fat, carbs) shifts over time.")
    df_daily["Protein Cal"] = df_daily["Protein (g)"] * 4
    df_daily["Carb Cal"] = df_daily["Carbohydrates (g)"] * 4
    df_daily["Fat Cal"] = df_daily["Fat (g)"] * 9
    df_daily["Total Macro Cal"] = df_daily["Protein Cal"] + df_daily["Carb Cal"] + df_daily["Fat Cal"]
    df_daily["Protein Ratio"] = df_daily["Protein Cal"] / df_daily["Total Macro Cal"]
    df_daily["Carb Ratio"] = df_daily["Carb Cal"] / df_daily["Total Macro Cal"]
    df_daily["Fat Ratio"] = df_daily["Fat Cal"] / df_daily["Total Macro Cal"]
    fig4, ax4 = plt.subplots(figsize=(10, 4))
    df_plot = df_daily[["Date", "Protein Ratio", "Carb Ratio", "Fat Ratio"]].set_index("Date").rolling(7).mean()
    df_plot.plot(ax=ax4)
    ax4.set_title("7-Day Rolling Macro Ratio Trend")
    ax4.set_ylabel("Ratio")
    st.pyplot(fig4)
    download_figure(fig4, "macro_ratio_trends.png")

    st.subheader("Meal Breakdown")
    if "Meal" in df_raw.columns:
        meal_totals = df_raw.groupby("Meal")["Calories"].sum()
        total_calories = meal_totals.sum()
        meal_percent = (meal_totals / total_calories * 100).sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=meal_percent.index, y=meal_percent.values, ax=ax)
        ax.set_ylabel("Calorie Share (%)")
        ax.set_title("Calorie Distribution by Meal Type")
        ax.set_ylim(0, 100)
        for i, v in enumerate(meal_percent.values):
            ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
        st.pyplot(fig)
        download_figure(fig, "meal_breakdown_percent.png")
    else:
        st.info("No 'Meal' column found in CSV.")

