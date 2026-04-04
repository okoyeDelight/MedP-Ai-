import streamlit as st
import google.generativeai as genai
import re
import urllib.parse

# 1. SETUP - Putting the key directly in the code to fix the error
API_KEY = "AIzaSyDScvVrWLB_KzagEm517qV6BTeyQfhpbUY" 
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Herbal AI Guide", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.write("Enter a symptom to find a botanical household remedy.")

expert_prompt = "You are a Pharmacognosy expert. Give: 1. Plant Name, 2. Source, 3. Preparation, 4. Safety. End with 'SEARCH_TERM: [Plant Name]'"

user_input = st.text_input("What is your symptom?")

if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Searching..."):
            try:
                # Using the older, most stable "Pro" model
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(f"{expert_prompt}\n\nSymptom: {user_input}")
                
                text = response.text
                st.success("Remedy Found!")
                st.markdown(text)
                
                # Image search link logic
                match = re.search(r"SEARCH_TERM:\s*(.+)", text)
                if match:
                    plant = urllib.parse.quote(match.group(1).strip() + " plant")
                    st.markdown(f"**[View Images on Google](https://www.google.com/search?tbm=isch&q={plant})**")
            except Exception as e:
                st.error(f"Error: {e}")
                
