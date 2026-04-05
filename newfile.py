import streamlit as st
import google.generativeai as genai

# 1. Setup
genai.configure(api_key="AIzaSyDScvVrWLB_KzagEm517qV6BTeyQfhpbUY")

st.set_page_config(page_title="Herbal AI", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.write("Pharmacognosy Assistant")

# 2. Input
user_input = st.text_input("What is the symptom?")

# 3. Search Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Analyzing..."):
            try:
                model = genai.GenerativeModel('gemini-3-flash-preview')
                prompt = f"You are a Pharmacognosy expert. Provide a layman herbal remedy for {user_input} with plant name, preparation, and safety."
                response = model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a symptom.")
        
