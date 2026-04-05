import streamlit as st
import google.generativeai as genai
import wikipedia

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") 

st.set_page_config(page_title="Herbal AI - Nigeria", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.subheader("Your Local Pharmacy Assistant")
st.write("Simple herbal guides using things you have for house.")

# 2. Input
user_input = st.text_input("Wetin dey do you? (Enter symptom):", placeholder="e.g., Malaria, Cold, Stomach ache")

# 3. Search & Generation Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Wait small, make I check my pharmacy book..."):
            try:
                # --- PART A: Text Generation (Gemini 3 Flash) ---
                text_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                # The "Household Measure" Prompt
                prompt = (
                    f"You are a friendly Nigerian Pharmacist explaining a herbal remedy for: {user_input}.\n\n"
                    "Please follow these instructions strictly:\n"
                    "1. Start with '### 🇳🇬 The Matter for Short (Pidgin Summary)' explaining the remedy in easy Pidgin.\n"
                    "2. Use 'Small English' for the rest—no big grammar.\n"
                    "3. For measurements, DO NOT use 'ml' or 'grams' alone. Always use household equipment like:\n"
                    "   - 'One teaspoon' (for small dose)\n"
                    "   - 'One standard tea cup' or 'Bournvita cup'\n"
                    "   - 'Half of a small Coca-Cola bottle' (for 25cl/35cl)\n"
                    "   - 'One sachet water bag' or 'One big Eva water bottle' (for 50cl/75cl)\n"
                    "4. Structure the response like this:\n"
                    "   - **Common & Botanical Name**\n"
                    "   - **Local Names**: (Igbo, Yoruba, and Hausa)\n"
                    "   - **How to prepare am**: (Step-by-step using cups/bottles)\n"
                    "   - **How to take am**: (Dosage using spoons/cups)\n"
                    "   - **Warning**: (Safety advice in simple English)\n\n"
                    "CRITICAL: At the very end, add exactly this line: BOTANICAL_NAME: [Latin Name Only]"
                )
                
                response = text_model.generate_content(prompt)
                st.success("I don find am!")
                st.markdown(response.text)

                # --- PART B: Wikipedia Image ---
                if "BOTANICAL_NAME:" in response.text:
                    latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip().replace("[", "").replace("]", "")
                    
                    with st.status(f"Looking for picture of {latin_name}...") as status:
                        try:
                            page = wikipedia.page(latin_name, auto_suggest=False)
                            plant_images = [img for img in page.images if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
                            
                            if plant_images:
                                st.image(plant_images[0], caption=f"This is the plant: {latin_name}", use_container_width=True)
                                status.update(label="Picture found!", state="complete")
                            else:
                                status.update(label="No clear picture found, but the info is above.", state="error")
                        except Exception:
                            status.update(label="Could not find the plant picture on Wikipedia.", state="error")

            except Exception as e:
                st.error(f"Technical Error: {e}")
    else:
        st.warning("Abeg, enter wetin dey do you first!")

# 4. Footer
st.divider()
st.caption("Developed by ®Desprix Crew ©2026. .")
            
