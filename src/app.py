import streamlit as st
from nutrition import show_nutrition_tab
from weight import show_weight_tab

st.set_page_config(page_title="MyFitnessPal Visualizer", layout="wide")
st.title("MyFitnessPal Data Visualizer")

# Session Reset
if st.sidebar.button("Clear Stored Data"):
    st.session_state.clear()
    st.rerun()

# Tabs
tab1, tab2 = st.tabs(["Nutrition Summary", "Weight Tracking"])

with tab1:
    show_nutrition_tab()

with tab2:
    show_weight_tab()
