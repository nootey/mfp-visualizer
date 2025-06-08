import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def download_figure(fig, filename="nutrition_plot.png"):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.download_button("Download Plot", data=buf.getvalue(), file_name=filename, mime="image/png")
    buf.close()

def show_nutrition_tab():
    st.header("Nutrition Summary")

    uploaded_file = st.file_uploader("Upload your Nutrition CSV", type=["csv"], key="nutrition_upload")
    if uploaded_file:
        st.session_state["nutrition_df"] = pd.read_csv(uploaded_file)

    nutrition_df = st.session_state.get("nutrition_df")

    if nutrition_df is not None:
        nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"])
        nutrition_df = nutrition_df.sort_values("Date")

        st.subheader("Daily Calorie Intake")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=nutrition_df, x="Date", y="Calories", ax=ax1)
        ax1.set_ylabel("Calories")
        ax1.set_xlabel("Date")
        st.pyplot(fig1)
        download_figure(fig1, "calories_over_time.png")

        st.subheader("Nutrient Distributions")
        nutrient_cols = ["Fat (g)", "Saturated Fat", "Carbohydrates (g)", "Protein (g)", "Sugar"]
        for col in nutrient_cols:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(nutrition_df[col].dropna(), kde=True, ax=ax)
            ax.set_title(f"{col} Distribution")
            st.pyplot(fig)
            download_figure(fig, f"{col.replace(' ', '_').lower()}_hist.png")

        st.subheader("Nutrient Correlation Heatmap")
        heatmap_df = nutrition_df.select_dtypes(include=["float64", "int64"])
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.heatmap(heatmap_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax3)
        ax3.set_title("Correlation Matrix")
        st.pyplot(fig3)
        download_figure(fig3, "correlation_heatmap.png")
    else:
        st.info("Please upload a Nutrition CSV file to begin.")