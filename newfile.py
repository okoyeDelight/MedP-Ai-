import streamlit as st
import google.generativeai as genai

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
                # --- PART A: Text Generation (Gemini 3) ---
                text_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                # Refined prompt for Nigerian context
                prompt = (
                    f"You are a Pharmacognosy expert specializing in Nigerian medicinal plants. "
                    f"Provide a herbal remedy for: {user_input}.\n\n"
                    "Structure your response with these headings:\n"
                    "1. **Common Name**\n"
                    "2. **Botanical Name**\n"
                    "3. **Local Nigerian Names** (List Igbo, Yoruba, and Hausa names clearly)\n"
                    "4. **Active Constituents** (e.g., Alkaloids, Tannins, Flavonoids)\n"
                    "5. **Preparation & Usage**\n"
                    "6. **Safety & Contraindications**\n\n"
                    "CRITICAL: At the very end of your response, add exactly this line: "
                    "BOTANICAL_NAME: [Latin Name Only]"
                )
                
                response = text_model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)

                # --- PART B: Image Generation (Imagen 3) ---
                # Check if the botanical name was provided for the image search
                if "BOTANICAL_NAME:" in response.text:
                    # Extract the Latin name
                    latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip()
                    
                    with st.status(f"Generating illustration for {latin_name}...") as status:
                        # Call the 2026 Image Model
                        img_model = genai.GenerativeModel('gemini-2.5-flash-image')
                        
                        img_prompt = (
                            f"A professional, scientific botanical illustration of {latin_name} "
                            "showing leaf detail and flowers on a clean white background. "
                            "High-resolution medical textbook style."
                        )
                        
                        img_result = img_model.generate_content(img_prompt)
                        
                        # Display the generated image
                        st.image(img_result.generated_images[0], 
                                 caption=f"Botanical Reference: {latin_name}", 
                                 use_container_width=True)
                        status.update(label="Visual identification loaded!", state="complete")

            except Exception as e:
                st.error(f"Technical Error: {e}")
                st.info("Check if your API key is restricted or if the model name is correct for your region.")
    else:
        st.warning("Please enter a symptom to begin the search.")

# 4. Footer
st.divider()
st.caption("Developed by ®Desprix Crew ©2026.")
