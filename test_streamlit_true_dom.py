import urllib.request
import time

def check():
    # Wait for the app to initialize
    time.sleep(8)
    try:
        # Streamlit serves the initial HTML which then loads React.
        # The DOM elements might be loaded dynamically.
        # Let's fetch the frontend source mapping or index to find elements related to ChatInput.
        with open("/usr/local/lib/python3.12/site-packages/streamlit/components/v1/components.py", "r") as f:
            pass
    except Exception as e:
        print(f"Error: {e}")

check()
