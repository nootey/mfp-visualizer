import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import download_figure, filter_date_range

def show_nutrition_tab():
    st.header("Nutrition Summary")

    uploaded_file = st.file_uploader("Upload your Nutrition CSV", type=["csv"], key="nutrition_upload")
    if uploaded_file:
        st.session_state["nutrition_df"] = pd.read_csv(uploaded_file)

    nutrition_df = st.session_state.get("nutrition_df")

    if nutrition_df is not None:
        nutrition_df = filter_date_range(nutrition_df)

        if nutrition_df.empty:
            st.warning("No data in selected date range.")
            return

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

        st.subheader("Nutrition Summary")
        days_logged = nutrition_df["Date"].nunique()
        avg_cal = nutrition_df["Calories"].mean()
        avg_protein = nutrition_df["Protein (g)"].mean()
        avg_fat = nutrition_df["Fat (g)"].mean()
        avg_carbs = nutrition_df["Carbohydrates (g)"].mean()
        max_day = nutrition_df.loc[nutrition_df["Calories"].idxmax()]
        min_day = nutrition_df.loc[nutrition_df["Calories"].idxmin()]

        st.markdown(f"""
        - **Days Logged:** {days_logged}
        - **Average Calories/day:** {avg_cal:.0f} kcal
        - **Average Protein:** {avg_protein:.1f} g
        - **Average Fat:** {avg_fat:.1f} g
        - **Average Carbs:** {avg_carbs:.1f} g
        - **Highest Calorie Day:** {max_day['Date'].date()} – {max_day['Calories']} kcal
        - **Lowest Calorie Day:** {min_day['Date'].date()} – {min_day['Calories']} kcal
        """)
    else:
        st.info("Please upload a Nutrition CSV file to begin.")