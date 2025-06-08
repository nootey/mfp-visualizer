from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt

def download_figure(fig, filename="plot.png"):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.download_button("Download Plot", data=buf.getvalue(), file_name=filename, mime="image/png")
    buf.close()

def filter_date_range(df, date_column="Date", key_prefix=""):
    df[date_column] = pd.to_datetime(df[date_column])
    min_date = df[date_column].min()
    max_date = df[date_column].max()

    today = pd.Timestamp.today()
    presets = {
        "This Week": today - timedelta(days=today.weekday()),
        "Last 2 Weeks": today - timedelta(days=14),
        "This Month": today.replace(day=1),
        "Past 2 Months": (today.replace(day=1) - pd.DateOffset(months=1)).replace(day=1),
        "This Year": datetime(today.year, 1, 1),
        "Past 2 Years": datetime(today.year - 2, 1, 1),
        "All Time": min_date
    }

    preset_labels = list(presets.keys())
    preset_default_index = preset_labels.index("Past 2 Months")

    preset_choice = st.selectbox(
        "Select a Date Range Preset",
        preset_labels,
        index=preset_default_index,
        key=f"{key_prefix}_preset"
    )

    use_custom = st.checkbox("Use Custom Date Range", value=False, key=f"{key_prefix}_custom")
    if use_custom:
        date_range = st.date_input("Select Custom Date Range", [presets["Past 2 Months"], today], key=f"{key_prefix}_dates")
        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
            return df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]
        else:
            st.warning("Please select both start and end dates.")
            return pd.DataFrame(columns=df.columns)
    else:
        start_date = presets[preset_choice]
        end_date = today
        return df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]
