import streamlit as st
import google.generativeai as genai
import wikipedia

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

# --- CSS: UI & ANIMATIONS ---
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
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2e7d32;
        transform: translateY(-3px);
        box-shadow: 0px 10px 20px rgba(46,125, 50, 0.3);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    .pro-header {
        color: #ffcc00;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        animation: pulse 3s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🌿 Med AI Menu")
app_mode = st.sidebar.selectbox("Choose a Service:", 
                                ["Find Remedy", "Drug-Herb Interaction (PRO)", "Drug Researcher (PRO)", "NAFDAC Verifier", "Marketplace"])

# --- TAB 1: FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    user_input = st.text_input("What is the symptom?", placeholder="e.g., Malaria, Cold")
    if st.button("Search Remedy"):
        if user_input:
            with st.spinner("Searching..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash') 
                    prompt = f"Friendly Pharmacist: Remedy for {user_input}. Pidgin summary at top. Household measures. End with BOTANICAL_NAME: [Latin]"
                    response = model.generate_content(prompt)
                    if response.text:
                        play_fx()
                        st.markdown(response.text)
                except Exception as e: st.error(f"Error: {e}")

# --- TAB 2: INTERACTION CHECKER ---
elif app_mode == "Drug-Herb Interaction (PRO)":
    st.markdown('<p class="pro-header">⚡ Interaction Checker</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: herb = st.text_input("Herb:")
    with col2: drug = st.text_input("Drug:")
    if st.button("Check Safety"):
        if herb and drug:
            with st.spinner("Analyzing..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"Pharmacist: Interaction {herb} + {drug}. Safe or Dangerous? Pidgin summary.")
                st.warning(response.text)

# --- TAB 3: DRUG RESEARCHER ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & Analysis</p>', unsafe_allow_html=True)
    target_drug = st.text_input("Enter Drug Name (e.g. Augmentin):")
    if st.button("Deconstruct Drug"):
        if target_drug:
            with st.spinner("Analyzing API..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"Clinical Pharmacologist: Break down {target_drug} (API, Mechanism, Contraindications, Generics, Side effects)."
                response = model.generate_content(prompt)
                st.success(response.text)

# --- TAB 4: NAFDAC VERIFIER (STABLE 2026 SYNTAX) ---
elif app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    st.write("Verifying registration numbers using live Google Search grounding.")
    
    reg_num = st.text_input("Enter NAFDAC Reg No:", placeholder="e.g., A11-1162")
    
    if st.button("Verify Registration"):
        if reg_num:
            with st.spinner(f"Scanning live records for {reg_num}..."):
                try:
                    # THE FIX: 1. Use the full models/ path. 2. Use the dictionary tool.
                    model = genai.GenerativeModel(
                        model_name='models/gemini-2.5-flash',
                        tools=[{"google_search": {}}] 
                    )

                    prompt = (
                        f"Search the internet for the NAFDAC registration number: {reg_num}.\n\n"
                        "1. Identify the exact product name and manufacturer.\n"
                        "2. Explain the prefix (e.g., A1, B4).\n"
                        "3. Give a clear 'Likely Authentic' or 'Unverified' status.\n"
                        "4. Include the link to the official NAFDAC portal."
                    )
                    
                    response = model.generate_content(prompt)
                    
                    if response and hasattr(response, 'text'):
                        play_fx()
                        st.success(f"Results found for: {reg_num}")
                        st.markdown(response.text)
                    else:
                        st.error("Live search returned no data. Check the number or NAFDAC portal.")
                        
                except Exception as e:
                    # If it still says "Unknown field", the library update in Step 1 didn't finish!
                    st.error(f"Search Error: {e}")
                    st.info("Ayo, make sure you updated requirements.txt and rebooted the app in Streamlit Cloud!")
        else:
            st.warning("Please enter a registration number.")
            
# --- TAB 5: MARKETPLACE ---
elif app_mode == "Marketplace":
    st.title("🛒 Marketplace")
    st.write("Verified listings coming soon.")

st.sidebar.divider()
st.sidebar.caption("®Desprix Crew ©2026")
    
