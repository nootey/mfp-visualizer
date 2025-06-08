import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import download_figure, filter_date_range

def show_weight_tab():
    st.header("Weight Progress")

    uploaded_file = st.file_uploader("Upload your Weight CSV", type=["csv"], key="weight_upload")
    if uploaded_file:
        st.session_state["weight_df_raw"] = pd.read_csv(uploaded_file)

    # Only proceed if we have raw data
    weight_df_raw = st.session_state.get("weight_df_raw")
    if weight_df_raw is None:
        st.info("Please upload a Weight CSV file to begin.")
        return

    # Ask for source and display units
    source_unit = st.selectbox("What unit is your weight data in?", options=["kg", "lb"], key="unit_source")
    display_unit = st.selectbox("Select display unit", options=["kg", "lb"], key="unit_display")

    weight_df = weight_df_raw.copy()
    weight_df["Date"] = pd.to_datetime(weight_df["Date"])

    # Convert to display unit if needed
    if source_unit == "lb" and display_unit == "kg":
        weight_df["Display Weight"] = weight_df["Weight"] * 0.453592
    elif source_unit == "kg" and display_unit == "lb":
        weight_df["Display Weight"] = weight_df["Weight"] / 0.453592
    else:
        weight_df["Display Weight"] = weight_df["Weight"]

    # Apply date filter
    weight_df = filter_date_range(weight_df)

    if weight_df.empty:
        st.warning("No data in selected date range.")
        return

    # Plot weight over time
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=weight_df, x="Date", y="Display Weight", marker="o", ax=ax)
    ax.set_title(f"Weight Over Time ({display_unit})")
    ax.set_ylabel(f"Weight ({display_unit})")
    ax.set_xlabel("Date")
    st.pyplot(fig)
    download_figure(fig, "weight_over_time.png")

    # Summary statistics
    st.subheader("Weight Summary")
    num_entries = len(weight_df)
    start_date = weight_df["Date"].iloc[0].date()
    end_date = weight_df["Date"].iloc[-1].date()
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
