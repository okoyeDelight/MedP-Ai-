import streamlit as st
import google.generativeai as genai
import re
import urllib.parse

# 1. SETUP - Putting the key here fixes the "No place to put API key" issue
genai.configure(api_key="AIzaSyDScvVrWLB_KzagEm517qV6BTeyQfhpbUY")

st.set_page_config(page_title="Herbal Remedy AI", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.write("Enter a symptom to search global botanical texts for a layman household remedy.")

# The prompt that makes it act like a Pharmacognosy expert
expert_prompt = """
You are a world-class expert in Pharmacognosy. Provide:
1. Plant Name: Common and Scientific.
2. Global Source: Mention pharmacopoeia documents.
3. Preparation: Household layman terms.
4. Safety: Crucial warnings.
At the end, add: SEARCH_TERM: [Plant Name]
"""

user_input = st.text_input("What is your symptom?", placeholder="e.g. Cold, Fever")

if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Searching global texts..."):
            try:
                # We use 1.5-flash because it is the most stable for free users
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"{expert_prompt}\n\nSymptom: {user_input}")
                
                text = response.text
                st.success("Analysis Complete!")
                st.markdown(text)
                
                # Image search logic
                match = re.search(r"SEARCH_TERM:\s*(.+)", text)
                if match:
                    plant = urllib.parse.quote(match.group(1).strip())
                    st.markdown(f"**[View Images on Google](https://www.google.com/search?tbm=isch&q={plant}+plant)**")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a symptom.")
except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a symptom first.")

st.sidebar.info("This is a pharmacy student project for educational purposes, innofest 26.")

