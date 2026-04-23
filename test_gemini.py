import google.generativeai as genai
import os
import sys

# Try different ways to init model
try:
    model = genai.GenerativeModel('models/gemini-2.5-flash', tools=[{"google_search": {}}])
    print("Init successful")
except Exception as e:
    print(f"Init error: {e}")
