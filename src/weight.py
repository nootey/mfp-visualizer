import os

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import download_figure, filter_date_range

def show_weight_tab():
    st.header("Weight Progress")

    uploaded_file = st.file_uploader("Upload your Weight CSV", type=["csv"], key="weight_upload")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/weight_latest.csv", index=False)
        st.session_state["weight_df_raw"] = df
        st.success("File uploaded and saved.")
    elif os.path.exists("data/weight_latest.csv"):
        df = pd.read_csv("data/weight_latest.csv")
        st.session_state["weight_df_raw"] = df
        st.info("Using previously saved weight data.")
    else:
        st.warning("Please upload a Weight CSV file to begin.")

    weight_df_raw = st.session_state.get("weight_df_raw")
    if weight_df_raw is None:
        st.info("Please upload a Weight CSV file to begin.")
        return

    source_unit = st.selectbox("What unit is your weight data in?", options=["kg", "lb"], key="unit_source")
    display_unit = st.selectbox("Select display unit", options=["kg", "lb"], key="unit_display")

    weight_df = weight_df_raw.copy()
    weight_df["Date"] = pd.to_datetime(weight_df["Date"])

    # Unit conversion
    if source_unit == "lb" and display_unit == "kg":
        weight_df["Display Weight"] = weight_df["Weight"] * 0.453592
    elif source_unit == "kg" and display_unit == "lb":
        weight_df["Display Weight"] = weight_df["Weight"] / 0.453592
    else:
        weight_df["Display Weight"] = weight_df["Weight"]

    # Filter by date
    weight_df = filter_date_range(weight_df, key_prefix="weight")

    if weight_df.empty:
        st.warning("No data in selected date range.")
        return

    start_date = weight_df["Date"].iloc[0].date()
    end_date = weight_df["Date"].iloc[-1].date()

    # Weight Graph
    st.subheader("Weight Over Time")
    st.caption("Your daily weight trend over the selected date range.")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=weight_df, x="Date", y="Display Weight", marker="o", ax=ax)
    ax.set_title(f"Weight Over Time ({display_unit})")
    ax.set_ylabel(f"Weight ({display_unit})")
    ax.set_xlabel("Date")
    st.pyplot(fig)
    download_figure(fig, "weight_over_time.png")

    # Summary Stats
    st.subheader("Weight Summary")
    st.caption("How your weight changed in this date range.")
    num_entries = len(weight_df)
    start_weight = weight_df["Display Weight"].iloc[0]
    end_weight = weight_df["Display Weight"].iloc[-1]
    delta = end_weight - start_weight
    delta_str = f"{delta:+.1f} {display_unit}"
    direction = "Increase" if delta > 0 else "Decrease" if delta < 0 else "No Change"
    days = (weight_df["Date"].iloc[-1] - weight_df["Date"].iloc[0]).days
    rate = delta / days if days > 0 else 0

    st.markdown(f"""
    - **Entries Logged:** {num_entries}
    - **Date Range:** {start_date} to {end_date}
    - **Start Weight:** {start_weight:.1f} {display_unit}
    - **End Weight:** {end_weight:.1f} {display_unit}
    - **Change:** {direction} ({delta_str})
    - **Average Change/Day:** {rate:+.3f} {display_unit}/day
    """)

    # Logging Streak
    st.subheader("Logging Streaks and Coverage")
    st.caption("Most consistent tracking and coverage over the selected time.")
    all_dates = pd.date_range(weight_df["Date"].min(), weight_df["Date"].max())
    logged_dates = pd.to_datetime(weight_df["Date"].unique())
    gaps = all_dates.difference(logged_dates)
    gap_days = len(gaps)
    total_days = len(all_dates)
    log_coverage = 100 * (total_days - gap_days) / total_days

    streaks = (weight_df["Date"].diff().dt.days != 1).cumsum()
    longest_streak = weight_df.groupby(streaks).size().max()

    st.markdown(f"""
    - **Longest Logging Streak:** {longest_streak} days
    - **Days Tracked:** {total_days - gap_days}
    - **Total Days in Range:** {total_days}
    - **Tracking Coverage:** {log_coverage:.1f}%
    """)

    # Peaks & Patterns
    if days >= 30:
        st.subheader("Peaks and Patterns")
        st.caption("Weeks where your weight was most stable or volatile, and weekday trends.")

        weight_df["Week Start"] = weight_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly_sd = weight_df.groupby("Week Start")["Display Weight"].std().dropna()

        most_consistent_week = weekly_sd.idxmin()
        least_consistent_week = weekly_sd.idxmax()

        st.markdown(f"""
        - **Most Consistent Week:** {most_consistent_week.date()} — Std Dev: {weekly_sd.min():.2f} {display_unit}
        - **Most Volatile Week:** {least_consistent_week.date()} — Std Dev: {weekly_sd.max():.2f} {display_unit}
        """)

        # Largest daily change (context-aware)
        st.markdown("### Largest Daily Change")
        st.caption("Only considers changes where you've logged at least 3 entries within a 2-week period. Below that, the full-data max is also shown.")

        weight_df["Delta"] = weight_df["Display Weight"].diff()

        # Filter for 14-day windows with at least 3 entries
        valid_dates = []
        for i, row in weight_df.iterrows():
            window = weight_df[(weight_df["Date"] >= row["Date"] - pd.Timedelta(days=7)) &
                               (weight_df["Date"] <= row["Date"] + pd.Timedelta(days=7))]
            if len(window) >= 3:
                valid_dates.append(i)

        if valid_dates:
            deltas_valid = weight_df.loc[valid_dates]
            largest_valid_idx = deltas_valid["Delta"].abs().idxmax()
            largest_valid_row = weight_df.loc[largest_valid_idx]
            st.markdown(f"- **Most Meaningful Change:** {largest_valid_row['Delta']:+.2f} {display_unit} on {largest_valid_row['Date'].date()}")
        else:
            st.warning("Not enough dense data to compute a meaningful largest change in a 2-week window.")

        # Still show full max change
        full_largest_idx = weight_df["Delta"].abs().idxmax()
        full_largest_row = weight_df.loc[full_largest_idx]
        st.markdown(f"- **Largest Change (all-time):** {full_largest_row['Delta']:+.2f} {display_unit} on {full_largest_row['Date'].date()}")


        # Weekday pattern
        weight_df["Weekday"] = weight_df["Date"].dt.day_name()
        weekday_avg = weight_df.groupby("Weekday")["Display Weight"].mean()
        weekday_avg = weekday_avg.reindex([
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ])

        fig3, ax3 = plt.subplots(figsize=(8, 4))
        sns.barplot(x=weekday_avg.index, y=weekday_avg.values, ax=ax3)
        ax3.set_title("Average Weight by Weekday")
        ax3.set_ylabel(f"Weight ({display_unit})")
        ax3.set_xlabel("Day of Week")
        st.pyplot(fig3)
        download_figure(fig3, "weekday_patterns.png")

    # Quarterly Comparison
    if days >= 365:
        st.subheader("Quarterly Comparison")
        st.caption("Weight statistics per quarter for each year in the selected data.")

        weight_df["Quarter"] = weight_df["Date"].dt.to_period("Q")
        quarterly_stats = weight_df.groupby("Quarter")["Display Weight"].agg(["first", "last", "mean"])
        quarterly_stats["Change"] = quarterly_stats["last"] - quarterly_stats["first"]
        quarterly_stats_display = quarterly_stats.rename(columns={
            "first": "Start",
            "last": "End",
            "mean": "Average"
        }).round(2)

        # Show table
        st.dataframe(quarterly_stats_display)

        # Line chart: change over quarters
        st.caption("Quarterly change in weight over time.")
        fig_q, ax_q = plt.subplots(figsize=(10, 4))
        quarters_as_str = quarterly_stats.index.astype(str)
        sns.barplot(x=quarters_as_str, y=quarterly_stats["Change"], ax=ax_q)
        ax_q.axhline(0, color="gray", linestyle="--")
        ax_q.set_ylabel(f"Quarterly Change ({display_unit})")
        ax_q.set_xlabel("Quarter")
        ax_q.set_title("Net Weight Change per Quarter")
        plt.xticks(rotation=45)
        st.pyplot(fig_q)
        download_figure(fig_q, "quarterly_changes.png")

    # Monthly Summary
    st.subheader("Monthly Summary")
    st.caption("Month-by-month breakdown of starting, ending, and average weight.")
    weight_df["Month"] = weight_df["Date"].dt.to_period("M")
    monthly_stats = weight_df.groupby("Month")["Display Weight"].agg(["first", "last", "mean"])
    monthly_stats["Change"] = monthly_stats["last"] - monthly_stats["first"]
    st.dataframe(monthly_stats.rename(columns={
        "first": "Start",
        "last": "End",
        "mean": "Average"
    }).round(2))

    # Rolling Averages
    st.subheader("Rolling Average and Weekly Averages")
    st.caption("Smoothed weight trends using 7-day rolling average and weekly means.")
    weight_df["Week"] = weight_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_avg = weight_df.groupby("Week")["Display Weight"].mean().reset_index(name="Weekly Avg")
    weight_df["7d Rolling Avg"] = weight_df["Display Weight"].rolling(window=7).mean()

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=weight_df, x="Date", y="Display Weight", label="Daily", ax=ax2)
    sns.lineplot(data=weight_df, x="Date", y="7d Rolling Avg", label="7-Day Avg", ax=ax2)
    sns.lineplot(data=weekly_avg, x="Week", y="Weekly Avg", label="Weekly Avg", linestyle='--', ax=ax2)
    ax2.set_title("Weight Trends")
    ax2.set_ylabel(f"Weight ({display_unit})")
    ax2.set_xlabel("Date")
    ax2.legend()
    st.pyplot(fig2)
    download_figure(fig2, "weight_trends.png")

    # Volatility
    st.subheader("Weight Volatility")
    st.caption("How much your weight fluctuates — lower standard deviation means more consistency.")
    std_dev = weight_df["Display Weight"].std()
    st.markdown(f"- **Standard Deviation:** {std_dev:.2f} {display_unit}")
