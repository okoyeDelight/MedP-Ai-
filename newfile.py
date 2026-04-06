import streamlit as st
import google.generativeai as genai
import wikipedia
import base64

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") 

st.set_page_config(page_title="Desprix Med AI", page_icon="🌿", layout="wide")

# --- SOUND FX FUNCTION ---
def play_fx():
    sound_url = "https://www.soundjay.com/buttons/sounds/button-37.mp3"
    st.components.v1.html(
        f"""
        <audio autoplay>
            <source src="{sound_url}" type="audio/mpeg">
        </audio>
        """,
        height=0,
    )

# --- CSS: ANIMATIONS & UI ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #1b5e20;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        background-color: #2e7d32;
        transform: scale(1.02) translateY(-5px);
        box-shadow: 0px 12px 24px rgba(46, 125, 50, 0.4);
    }

    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 0px rgba(255, 204, 0, 0); }
        50% { transform: scale(1.03); text-shadow: 0 0 10px rgba(255, 204, 0, 0.5); }
        100% { transform: scale(1); text-shadow: 0 0 0px rgba(255, 204, 0, 0); }
    }
    .pro-header {
        color: #ffcc00;
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        animation: pulse 3s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🌿 Med AI Menu")
# FIXED: Ensuring these strings match the logic below perfectly
app_mode = st.sidebar.selectbox("Choose a Service:", 
                                ["Find Remedy", "Drug-Herb Interaction (PRO)", "Drug Researcher (PRO)", "Marketplace"])

# --- TAB 1: FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    user_input = st.text_input("What is the symptom?", placeholder="e.g., Malaria, Cold")

    if st.button("Search Remedy"):
        if user_input:
            with st.spinner("Analyzing..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash') 
                    prompt = (
                        f"You are a friendly Pharmacist. Explain a herbal remedy for: {user_input}. "
                        "Include '### 🇳🇬 Summary' in Pidgin. Use simple English and household measures. "
                        "Do not mention specific universities. End with: BOTANICAL_NAME: [Latin Name Only]"
                    )
                    response = model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        play_fx() 
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: INTERACTION CHECKER ---
elif app_mode == "Drug-Herb Interaction (PRO)":
    st.markdown('<p class="pro-header">⚡ Interaction Checker</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: herb = st.text_input("Herb Name:")
    with col2: drug = st.text_input("Drug Name:")
    if st.button("Run Safety Check"):
        if herb and drug:
            with st.spinner("Checking..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"Pharmacist Analysis: Interaction between {herb} and {drug}. Use simple English and Pidgin summary. Do not mention specific schools."
                    response = model.generate_content(prompt)
                    st.warning(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 3: FIXED! DRUG RESEARCHER (PRO) ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & Analysis</p>', unsafe_allow_html=True)
    st.write("Deep breakdown of pharmaceutical components and generic alternatives.")
    
    target_drug = st.text_input("Enter Drug Name for Analysis:", placeholder="e.g., Amatem, Augmentin, Lisinopril")

    if st.button("Deconstruct Drug"):
        if target_drug:
            with st.spinner(f"Deconstructing {target_drug}..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    safety = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
                    
                    prompt = (
                        f"You are a Clinical Pharmacologist. Provide a deep research breakdown for the drug: {target_drug}.\n\n"
                        "Structure your response exactly like this:\n"
                        "1. **API Breakdown**: List the Active Pharmaceutical Ingredient(s).\n"
                        "2. **Mechanism of Action**: Explain what it does in the body (how it works).\n"
                        "3. **Indications**: What is it used for?\n"
                        "4. **Contraindications**: Who should NEVER take this drug?\n"
                        "5. **Generic Versions**: List common generic alternatives that are more cost-effective.\n"
                        "6. **Side Effects**: What should the user watch out for?\n\n"
                        "Use professional but clear English. Do not mention any specific university."
                    )
                    
                    response = model.generate_content(prompt, safety_settings=safety)
                    if response and hasattr(response, 'text'):
                        play_fx()
                        st.success(f"Analysis for {target_drug} Complete")
                        st.markdown(response.text)
                    else:
                        st.error("System could not generate a response. Try a different drug name.")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
        else:
            st.warning("Please enter a drug name to analyze.")

# --- TAB 4: MARKETPLACE ---
elif app_mode == "Marketplace":
    st.title("🛒 Marketplace")
    st.link_button("Apply to Sell", "https://forms.gle/your-link")
    st.write("Verified listings coming soon.")

st.sidebar.divider()
st.sidebar.caption("®Desprix Crew ©2026")
    
