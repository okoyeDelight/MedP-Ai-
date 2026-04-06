import streamlit as st
import google.generativeai as genai
import wikipedia

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") 

st.set_page_config(page_title="Herbal AI Plus", page_icon="🌿", layout="wide")

# --- NAVIGATION ---
st.sidebar.title("🌿 Desprix Menu")
app_mode = st.sidebar.selectbox("Choose wetin you wan do:", 
                                ["Find Remedy", "Drug-Herb Interaction (PRO)", "Marketplace"])

# --- TAB 1: FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    user_input = st.text_input("Wetin dey do you?", placeholder="e.g., Malaria, Cold")

    if st.button("Search Remedy"):
        if user_input:
            with st.spinner("Checking records..."):
                try:
                    # Using Flash for speed and quota stability
                    model = genai.GenerativeModel('gemini-2.5-flash') 
                    prompt = (
                        f"You are a friendly Nigerian Pharmacist. Explain a remedy for: {user_input}. "
                        "Top section: '### 🇳🇬 The Matter for Short' in Pidgin. "
                        "Next: Use small English and household measures (cups, spoons, Coke bottles). "
                        "End with: BOTANICAL_NAME: [Latin Name Only]"
                    )
                    response = model.generate_content(prompt)
                    
                    # --- THE FIX: Check if AI actually sent text ---
                    if response and hasattr(response, 'text') and response.text:
                        st.markdown(response.text)
                        
                        # Image Logic
                        if "BOTANICAL_NAME:" in response.text:
                            latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip().replace("[", "").replace("]", "")
                            try:
                                page = wikipedia.page(latin_name, auto_suggest=False)
                                if page.images:
                                    st.image(page.images[0], caption=f"Specimen: {latin_name}", use_container_width=True)
                            except:
                                st.info("Picture not found, but remedy is above!")
                    else:
                        st.error("The AI is a bit shy right now (Safety/Quota). Try again in 1 minute.")
                except Exception as e:
                    st.error(f"Technical Glitch: {e}")
        else:
            st.warning("Type something first, Senior Man!")

# --- TAB 2: PRO INTERACTION ---
elif app_mode == "Drug-Herb Interaction (PRO)":
    st.title("⚡ Interaction Checker (PRO)")
    col1, col2 = st.columns(2)
    with col1: herb = st.text_input("Herb Name:")
    with col2: drug = st.text_input("Hospital Medicine:")
    
    if st.button("Check Safety"):
        if herb and drug:
            with st.spinner("Analyzing..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Pharmacognosy check: Can I take {herb} with {drug}? Explain in small English if it is safe. Mention side effects."
                    response = model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        st.warning("### ⚠️ Pharmacist Advice:")
                        st.markdown(response.text)
                except:
                    st.error("Could not complete check. Try again later.")

# --- TAB 3: MARKETPLACE ---
elif app_mode == "Marketplace":
    st.title("🛒 Supplements Corner")
    st.write("Buy verified products from Desprix partners.")
    st.link_button("Apply to Sell", "https://forms.gle/your-form-link")
    st.divider()
    st.write("Product listings coming soon to Agulu campus!")

st.sidebar.divider()
st.sidebar.caption("®Desprix Crew ©2026 | UNIZIK Pharmacy")
