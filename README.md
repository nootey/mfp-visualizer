# mfp-visualizer

An analytics dashboard for exploring and understanding your health data exported from MyFitnessPal. 
View trends, analyze macro distributions, track your weight progress, and correlate calorie intake with body changes.

- This project was made to analyze my own MFP data and display some useful trends.
- I also used Streamlit for the first time, to quickly serve it

## Pre-requisites

- To get your data, request a data export in the MFP app
- Go to progress -> export icon in the top right
- Select All timme as the reporting period, so that you can select specific date ranges in this app
- You will receive the data via email
- Once uploaded, the app will automatically save them for future sessions, unless you upload new files

### Technical

- Python
- Ensure dependencies are installed: `pip install -r requirements/common.txt`
- Run the app: `python run.py` or directly: `streamlit run src/app.py`

## Features
- Daily, Weekly, Monthly Summaries 
- Downloadable Graphs and automatic file retention
- Date Range Filters with intelligent presets (e.g. “Last 2 Weeks”, “This Year”)
- Weight Trend Analysis with slope-based trend classification 
- Calories per kg Gained/Lost with automatic TDEE estimation 
- Lagged Calorie Correlation (how calories from past days affect weight)
- Meal & Macro Breakdown 
- Volatility Insights (macros & weight)

## Notes
- The app uses 7700 kcal ≈ 1 kg fat for weight-energy conversions. 
- CSVs are automatically saved into /data and reused until cleared.
