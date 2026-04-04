import streamlit as st
import re
import urllib.parse
from google import genai

# Set up the web page title
st.set_page_config(page_title="Herbal AI Guide", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.write("Enter a symptom to search global botanical texts for a layman household remedy.")

# 1. Securely load the AI from Streamlit Secrets
# Make sure you have GEMINI_API_KEY saved in your Streamlit app settings!
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

expert_prompt = """
You are a world-class expert in Pharmacognosy.
Structure your response clearly:
1. Plant Name: Common name and Scientific name.
2. Global Source: Mention which pharmacopoeia documents this.
3. Preparation: STRICTLY HOUSEHOLD LAYMAN TERMS. NO MEDICAL JARGON. 
4. Contraindications & Safety: Crucial safety warnings.

CRITICAL INSTRUCTION: At the very end, provide ONLY the common name formatted EXACTLY like this:
SEARCH_TERM: [Insert Plant Name here]
"""

# Create the text input box for the user
user_input = st.text_input("What is your symptom?", placeholder="e.g. mild fever")

# Create a clickable web button
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Searching global texts..."):
            try:
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=dict(system_instruction=expert_prompt)
                )
                response = chat.send_message(user_input)
                text = response.text
                
                search_term_match = re.search(r"SEARCH_TERM:\s*(.+)", text)
                
                if search_term_match:
                    plant_name = search_term_match.group(1).strip()
                    clean_text = re.sub(r"SEARCH_TERM:\s*.+", "", text).strip()
                    encoded_plant = urllib.parse.quote(plant_name + " plant leaves")
                    google_image_url = f"https://www.google.com/search?tbm=isch&q={encoded_plant}"
                else:
                    google_image_url = None
                    clean_text = text
                
                # Display the AI response
                st.success("Remedy Found!")
                st.markdown(clean_text)
                
                if google_image_url:
                    st.markdown(f"**[Click here to view pictures of {plant_name} on Google Images]({google_image_url})**")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a symptom first.")
            
