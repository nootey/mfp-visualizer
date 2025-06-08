import subprocess
import os

# Path to your Streamlit app
app_path = os.path.join("src", "app.py")

# Launch Streamlit app
subprocess.run(["streamlit", "run", app_path])