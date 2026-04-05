import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. Setup & Security
# Ensure your API Key is stored in Streamlit Secrets as "GEMINI_API_KEY"
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Herbal AI - Nigeria", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.subheader("Pharmacognosy Assistant for Nigeria")
st.write("Supporting Pharmacy students with localized botanical insights.")

# 2. Input
user_input = st.text_input("What is the symptom?", placeholder="e.g., Cold, Malaria, Skin Rash")

# 3. Search & Generation Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Analyzing botanical data and local names..."):
            try:
                # --- PART A: Text Generation (Gemini 3.1 Flash) ---
                # Using the latest 2026 stable model for the "Brain"
                text_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                prompt = (
                    f"You are a Pharmacognosy expert specializing in Nigerian medicinal plants. "
                    f"Provide a herbal remedy for: {user_input}.\n\n"
                    "Structure your response with these headings:\n"
                    "1. **Common Name**\n"
                    "2. **Botanical Name**\n"
                    "3. **Local Nigerian Names** (List Igbo, Yoruba, and Hausa names clearly)\n"
                    "4. **Active Constituents**\n"
                    "5. **Preparation & Usage**\n"
                    "6. **Safety & Contraindications**\n\n"
                    "CRITICAL: At the very end of your response, add exactly this line: "
                    "BOTANICAL_NAME: [Latin Name Only]"
                )
                
                response = text_model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)

                # --- PART B: DuckDuckGo Image Search (No Quota Limits!) ---
                if "BOTANICAL_NAME:" in response.text:
                    # Extract the Latin name for the search query
                    latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip()
                    
                    with st.status(f"Searching for images of {latin_name}...") as status:
                        # We search for the Latin name + 'botanical illustration' for high quality
                        search_query = f"{latin_name} botanical medicinal plant illustration"
                        
                        with DDGS() as ddgs:
                            # We fetch the first 3 results to ensure we find a good one
                            results = ddgs.images(search_query, max_results=3)
                            
                            if results:
                                # Show the first valid image found
                                image_url = results[0]['image']
                                st.image(image_url, 
                                         caption=f"Botanical Identification: {latin_name}", 
                                         use_container_width=True)
                                status.update(label="Scientific image found!", state="complete")
                            else:
                                status.update(label="Could not find image, but data is above.", state="error")

            except Exception as e:
                st.error(f"Technical Error: {e}")
                st.info("Check your internet connection or API secret key.")
    else:
        st.warning("Please enter a symptom to begin the search.")

# 4. Footer
st.divider()
st.caption("Developed by ®Desprix Crew ©2026.")
                                
