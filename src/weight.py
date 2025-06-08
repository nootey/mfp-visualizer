import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def download_figure(fig, filename="weight_plot.png"):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.download_button("Download Plot", data=buf.getvalue(), file_name=filename, mime="image/png")
    buf.close()

def show_weight_tab():
    st.header("Weight Progress")

    uploaded_file = st.file_uploader("Upload your Weight CSV", type=["csv"], key="weight_upload")
    if uploaded_file:
        st.session_state["weight_df"] = pd.read_csv(uploaded_file)

    weight_unit = st.selectbox("Select Weight Unit", options=["kg", "lb"], key="unit_selector")
    conversion_factor = 0.453592 if weight_unit == "kg" else 1.0

    weight_df = st.session_state.get("weight_df")

    if weight_df is not None:
        weight_df["Date"] = pd.to_datetime(weight_df["Date"])
        weight_df = weight_df.sort_values("Date")
        weight_df["Display Weight"] = weight_df["Weight"] * conversion_factor

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=weight_df, x="Date", y="Display Weight", marker="o", ax=ax)
        ax.set_title(f"Weight Over Time ({weight_unit})")
        ax.set_ylabel(f"Weight ({weight_unit})")
        ax.set_xlabel("Date")
        st.pyplot(fig)
        download_figure(fig, "weight_over_time.png")
    else:
        st.info("Please upload a Weight CSV file to begin.")
