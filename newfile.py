                import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Setup & Security
# Ensure "GEMINI_API_KEY" is in your Streamlit Secrets!
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Herbal AI Nigeria", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.subheader("Pharmacognosy Assistant for Nigeria")

# 2. Input
user_input = st.text_input("What is the symptom?", placeholder="e.g., Malaria, Cold, Cough")

# 3. Search Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Consulting botanical records..."):
            try:
                # --- PART A: Text (Gemini 3.1 Flash) ---
                # Use the latest 2026 Flash model
                text_model = genai.GenerativeModel('gemini-3.1-flash')
                
                prompt = (
                    f"You are a Pharmacognosy expert in Nigeria. Provide a herbal remedy for: {user_input}.\n\n"
                    "Structure your response clearly with:\n"
                    "- **Botanical Name**\n"
                    "- **Local Names**: (Igbo, Yoruba, Hausa)\n"
                    "- **Preparation & Dosage**\n"
                    "- **Safety Note**\n\n"
                    "At the very end, add this exact line: BOTANICAL_NAME: [Latin Name Only]"
                )
                
                response = text_model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)

                # --- PART B: Image (Nano Banana 2 / Gemini 3.1 Flash Image) ---
                if "BOTANICAL_NAME:" in response.text:
                    latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip()
                    
                    with st.status(f"Generating illustration for {latin_name}...") as status:
                        # 2026 FIX: Use 'gemini-3.1-flash-image-preview' (Nano Banana 2)
                        img_model = genai.GenerativeModel('gemini-3.1-flash-image-preview')
                        
                        img_prompt = (
                            f"A professional scientific botanical illustration of {latin_name} "
                            "showing clear leaves and roots on a white background. "
                            "Medical textbook style, high resolution."
                        )
                        
                        img_response = img_model.generate_content(img_prompt)
                        
                        # In the 2026 SDK, we check parts for the generated image
                        for part in img_response.parts:
                            if hasattr(part, 'inline_data'):
                                # Convert the data to an image Streamlit can show
                                img = Image.open(io.BytesIO(part.inline_data.data))
                                st.image(img, caption=f"Botanical Identification: {latin_name}")
                        
                        status.update(label="Image loaded successfully!", state="complete")

            except Exception as e:
                st.error(f"Technical Error: {e}")
    else:
        st.warning("Please enter a symptom.")

st.divider()
st.caption("Developed by Desprix crew © 2026")
