import streamlit as st
import google.generativeai as genai
import wikipedia

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") # Set to English

st.set_page_config(page_title="Herbal AI - Nigeria", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.subheader("Pharmacognosy Assistant for Nigeria")
st.write("Supporting Pharmacy students with localized botanical insights.")

# 2. Input
user_input = st.text_input("What is the symptom?", placeholder="e.g., Malaria, Cold, Skin Rash")

# 3. Search & Generation Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Analyzing botanical data..."):
            try:
                # --- PART A: Text Generation (Gemini 3 Flash) ---
                text_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                prompt = (
                    f"You are a Pharmacognosy expert specializing in Nigerian medicinal plants. "
                    f"Provide a herbal remedy for: {user_input}.\n\n"
                    "Structure your response with these headings:\n"
                    "1. **Common Name**\n"
                    "2. **Botanical Name**\n"
                    "3. **Local Nigerian Names** (Igbo, Yoruba, and Hausa)\n"
                    "4. **Active Constituents**\n"
                    "5. **Preparation & Usage**\n"
                    "6. **Safety & Contraindications**\n\n"
                    "At the end, add exactly this line: BOTANICAL_NAME: [Latin Name Only]"
                )
                
                response = text_model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)

                # --- PART B: Wikipedia Image (Stable & Free) ---
                if "BOTANICAL_NAME:" in response.text:
                    latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip().replace("[", "").replace("]", "")
                    
                    with st.status(f"Fetching scientific image for {latin_name}...") as status:
                        try:
                            # Search for the plant page on Wikipedia
                            page = wikipedia.page(latin_name, auto_suggest=False)
                            
                            # Filter for actual plant images (usually .jpg or .png)
                            plant_images = [img for img in page.images if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
                            
                            if plant_images:
                                # Show the main image (usually the first one)
                                st.image(plant_images[0], caption=f"Scientific Specimen: {latin_name}", use_container_width=True)
                                status.update(label="Image found on Wikipedia!", state="complete")
                            else:
                                status.update(label="No clear image found on Wikipedia.", state="error")
                        except Exception:
                            status.update(label="Could not find a Wikipedia page for this plant.", state="error")

            except Exception as e:
                st.error(f"Technical Error: {e}")
    else:
        st.warning("Please enter a symptom first.")

# 4. Footer
st.divider()
st.caption("Developed by ®Desprix Crew ©2026.")

