import google.generativeai as genai
import os
from google.generativeai.types import Tool

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "DUMMY_KEY"))

try:
    model = genai.GenerativeModel('models/gemini-2.5-flash', tools='google_search_retrieval')
    print("Init successful with correct tool")
except Exception as e:
    print(f"Init error: {e}")
