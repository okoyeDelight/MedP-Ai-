import streamlit as st
import google.generativeai as genai
import wikipedia

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") 

st.set_page_config(page_title="Herbal AI Plus", page_icon="🌿", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🌿 Desprix Herbal Menu")
app_mode = st.sidebar.selectbox("Choose wetin you wan do:", 
                                ["Find Remedy", "Drug-Herb Interaction (PRO)", "Marketplace (Supplements)"])

# --- TAB 1: FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    st.write("Find natural remedies with 'Small English' and home measures.")
    
    user_input = st.text_input("Wetin dey do you? (e.g., Cold, Malaria)", placeholder="Type symptom here...")

    if st.button("Search Remedy"):
        if user_input:
            with st.spinner("Wait make I check my pharmacy book..."):
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    prompt = (
                        f"You are a friendly Nigerian Pharmacist. Explain a remedy for: {user_input}. "
                        "Include 'The Matter for Short' in Pidgin at the top. "
                        "Use ONLY small English and household measures (cups, spoons, Coke bottles). "
                        "At the end, add: BOTANICAL_NAME: [Latin Name Only]"
                    )
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    
                    # Wikipedia Image Logic
                    if "BOTANICAL_NAME:" in response.text:
                        latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip().replace("[", "").replace("]", "")
                        try:
                            page = wikipedia.page(latin_name, auto_suggest=False)
                            st.image(page.images[0], caption=f"Specimen: {latin_name}", use_container_width=True)
                        except: pass
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Enter symptom first.")

# --- TAB 2: PRO INTERACTION CHECKER ---
elif app_mode == "Drug-Herb Interaction (PRO)":
    st.title("⚡ Pro Feature: Interaction Checker")
    st.info("Check if your herbal tea goes well with your hospital medicine.")
    
    col1, col2 = st.columns(2)
    with col1:
        herb = st.text_input("Enter Herb Name:", placeholder="e.g., Ginger, Neem, Scent leaf")
    with col2:
        drug = st.text_input("Enter Hospital Medicine:", placeholder="e.g., Paracetamol, Warfarin, Aspirin")
    
    if st.button("Check Safety"):
        if herb and drug:
            with st.spinner("Analyzing pharmacological interactions..."):
                model = genai.GenerativeModel('gemini-3-flash-preview')
                prompt = (
                    f"As a Pharmacognosy expert, check the interaction between the herb '{herb}' and the drug '{drug}'. "
                    "Explain in simple terms if it is SAFE or DANGEROUS. "
                    "Mention possible side effects and give a clear advice for a layman. "
                    "Use Nigerian context if applicable."
                )
                response = model.generate_content(prompt)
                st.warning("### ⚠️ Pharmacist Advice:")
                st.markdown(response.text)
        else:
            st.warning("Please enter both the herb and the medicine name.")

# --- TAB 3: MARKETPLACE ---
elif app_mode == "Marketplace (Supplements)":
    st.title("🛒 Supplements Corner")
    st.write("Buy verified herbal products from trusted Nigerian sellers.")
    
    # Seller Application Button
    with st.expander("Are you a Seller? Place your product here!"):
        st.write("Submit your NAFDAC-approved products to join our marketplace.")
        # Link this to a Google Form for now
        st.link_button("Apply to Sell", "https://forms.gle/your-google-form-link")

    st.divider()
    
    # Marketplace Layout
    st.subheader("Featured Products")
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://via.placeholder.com/150", caption="Organic Neem Powder (1kg)")
        st.write("**Price:** ₦4,500")
        st.button("Buy Now", key="btn1")
        
    with col2:
        st.image("https://via.placeholder.com/150", caption="Pure Scent Leaf Oil (100ml)")
        st.write("**Price:** ₦3,000")
        st.button("Buy Now", key="btn2")

# --- FOOTER ---
st.sidebar.divider()
st.sidebar.caption("Developed by ®Desprix Crew ©2026.")
st.sidebar.write("Pharmacy Students, UNIZIK.")
