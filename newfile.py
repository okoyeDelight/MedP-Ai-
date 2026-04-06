import streamlit as st
import google.generativeai as genai
import wikipedia
import base64

# 1. Setup & Security
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
wikipedia.set_lang("en") 

st.set_page_config(page_title="Herbal AI Plus", page_icon="🌿", layout="wide")

# --- SOUND FX FUNCTION ---
def play_fx():
    # Subtle chime sound for success
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
    /* 1. Stop Pull-to-Refresh */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
    }

    /* 2. Button Animation: Glow and Lift */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        transform: scale(1.02) translateY(-5px);
        box-shadow: 0px 12px 24px rgba(46, 125, 50, 0.4);
    }
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* 3. Pulse Animation for PRO Feature */
    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 0px rgba(255, 204, 0, 0); }
        50% { transform: scale(1.05); text-shadow: 0 0 15px rgba(255, 204, 0, 0.6); }
        100% { transform: scale(1); text-shadow: 0 0 0px rgba(255, 204, 0, 0); }
    }
    .pro-header {
        color: #ffcc00;
        font-size: 32px;
        font-weight: 900;
        text-align: center;
        animation: pulse 2.5s infinite ease-in-out;
    }

    /* 4. Side-bar Menu Animation */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        transition: width 0.5s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
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
                    model = genai.GenerativeModel('gemini-2.5-flash') 
                    prompt = (
                        f"You are a friendly Nigerian Pharmacist. Explain a remedy for: {user_input}. "
                        "Top section: '### 🇳🇬 The Matter for Short' in Pidgin. "
                        "Next: Use small English and household measures (cups, spoons, Coke bottles). "
                        "End with: BOTANICAL_NAME: [Latin Name Only]"
                    )
                    response = model.generate_content(prompt)
                    
                    if response and hasattr(response, 'text') and response.text:
                        play_fx() # Trigger sound!
                        st.markdown(response.text)
                        
                        if "BOTANICAL_NAME:" in response.text:
                            latin_name = response.text.split("BOTANICAL_NAME:")[-1].strip().replace("[", "").replace("]", "")
                            try:
                                page = wikipedia.page(latin_name, auto_suggest=False)
                                if page.images:
                                    st.image(page.images[0], caption=f"Specimen: {latin_name}", use_container_width=True)
                            except:
                                st.info("Picture not found, but remedy is above!")
                    else:
                        st.error("The AI is a bit shy right now. Try again in 1 minute.")
                except Exception as e:
                    st.error(f"Technical Glitch: {e}")
        else:
            st.warning("Type something first, Senior Man!")

# --- TAB 2: PRO INTERACTION (ANIMATED) ---
elif app_mode == "Drug-Herb Interaction (PRO)":
    # Pulsing Pro Header
    st.markdown('<p class="pro-header">⚡ Interaction Checker (PRO)</p>', unsafe_allow_html=True)
    st.write("Checking safety between traditional herbs and hospital drugs.")
    
    col1, col2 = st.columns(2)
    with col1: herb = st.text_input("Herb Name (e.g., Dogonyaro):")
    with col2: drug = st.text_input("Hospital Medicine (e.g., Paracetamol):")
    
    if st.button("Check Safety"):
        if herb and drug:
            with st.spinner("Analyzing pharmacological data..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                    prompt = (
                        f"You are a Pharmacognosy Professor. Provide an educational analysis on the "
                        f"potential interaction between the herb '{herb}' and the drug '{drug}'.\n\n"
                        "1. Explain in simple English if there is a known interaction, use a little pidgin.\n"
                        "2. Use household terms (e.g., 'it fit make the drug work too much').\n"
                        "3. List potential side effects.\n"
                        "4. End with a strong disclaimer that this is for UNIZIK student research only."
                    )
                    response = model.generate_content(prompt, safety_settings=safety_settings)
                    
                    if response and hasattr(response, 'text'):
                        play_fx() # Trigger sound!
                        st.warning("### ⚠️ Still listen to a doctor:")
                        st.markdown(response.text)
                    else:
                        st.error("AI blocked the response for safety.")
                except Exception as e:
                    st.error(f"Technical Glitch: {e}")
        else:
            st.warning("Enter both names, Senior Man!")
                      
# --- TAB 3: MARKETPLACE ---
elif app_mode == "Marketplace":
    st.title("🛒 Supplements Corner")
    st.write("Buy verified products from Desprix partners.")
    st.link_button("Apply to Sell", "https://forms.gle/your-google-form-link")
    st.divider()
    st.write("Product listings coming soon to Agulu campus!")

st.sidebar.divider()
st.sidebar.caption("®Desprix Crew ©2026 | UNIZIK Pharmacy")
  
