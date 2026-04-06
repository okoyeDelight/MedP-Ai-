import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
from PIL import Image
import io

# 1. Setup & API Config
# Ensure GEMINI_API_KEY is in your Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Desprix Med AI", page_icon="🌿", layout="wide")

# --- CSS: PRO UI & ANIMATIONS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; color: white; }
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em;
        background-color: #1b5e20; color: #ffffff; font-weight: bold;
        border: 2px solid #2e7d32; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2e7d32; transform: scale(1.02); }
    .pro-header {
        color: #ffcc00; font-size: 32px; font-weight: 800;
        text-align: center; text-shadow: 2px 2px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'daily_score' not in st.session_state: st.session_state.daily_score = 0
if 'leaderboard' not in st.session_state: 
    st.session_state.leaderboard = pd.DataFrame(columns=['Name', 'Score', 'Status'])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🌿 Desprix 2.5 Ultimate")
app_mode = st.sidebar.selectbox("Choose a Service:", 
    ["Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Exam Mastery Hub", "Structure Master Class", "Leaderboard", "Marketplace"])

# --- 1. FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    u_input = st.text_input("What is the symptom?", placeholder="e.g. Fever, Malaria")
    if st.button("Search Remedy"):
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            resp = model.generate_content(f"Pharmacist: Remedy for {u_input} with Pidgin summary.")
            st.markdown(resp.text)
        except Exception as e: st.error(f"Error: {e}")

# --- 2. DRUG RESEARCHER (PRO) ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & API</p>', unsafe_allow_html=True)
    drug = st.text_input("Enter Drug Name:")
    if st.button("Analyze API"):
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"Pharmacologist: Deep breakdown of {drug} (API, Mechanism, Generics, Side effects)."
        resp = model.generate_content(prompt)
        st.success(resp.text)

# --- 3. NAFDAC VERIFIER ---
elif app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    reg = st.text_input("Enter NAFDAC Reg No:")
    if st.button("Verify Registration"):
        try:
            # THE 2.5 SEARCH FIX: Using the correct tool syntax
            model = genai.GenerativeModel(
                'models/gemini-2.5-flash', 
                tools=[{"google_search": {}}]
            )
            resp = model.generate_content(f"Verify NAFDAC registration: {reg}. Name product and manufacturer.")
            st.info(resp.text)
        except Exception as e: st.error(f"Search Error: {e}")

# --- 4. EXAM MASTERY HUB ---
elif app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Daily Quiz", "🎤 Lecture Analyst", "📝 Note-to-CBT"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        # Quiz logic here
        st.write("Question: Which drug class inhibits cell wall synthesis?")
        ans = st.radio("Pick:", ["NSAIDs", "Penicillins", "Statins"])
        if st.button("Submit"):
            if ans == "Penicillins": st.success("Correct!")
            else: st.error("Wrong!")

    with tab2:
        st.subheader("Lecture Secret Extractor (m4a/MP3/PDF)")
        aud = st.file_uploader("Upload Lecture Audio", type=['mp3', 'wav', 'm4a'])
        doc = st.file_uploader("Upload Class Handout", type=['pdf'])
        if aud and doc:
            if st.button("Analyze & Compare"):
                with st.spinner("Gemini 2.5 is listening..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        aud_bytes = aud.read()
                        m_type = "audio/mp4" if aud.name.endswith("m4a") else f"audio/{aud.type.split('/')[-1]}"
                        prompt = "Compare audio to handout. Find lecturer emphasis and give 5 exam questions with a Pidgin summary."
                        resp = model.generate_content([prompt, {"mime_type": m_type, "data": aud_bytes}])
                        st.markdown(resp.text)
                    except Exception as e: st.error(f"Error: {e}")

    with tab3:
        st.subheader("Interactive Note-to-CBT")
        note = st.file_uploader("Upload Notes (Image/PDF)", type=['png', 'jpg', 'pdf'])
        if note:
            if st.button("Generate CBT"):
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                st.success("CBT Questions Extracted!")

# --- 5. STRUCTURE MASTER CLASS ---
elif app_mode == "Structure Master Class":
    st.markdown('<p class="pro-header">🎨 Structure Cheats</p>', unsafe_allow_html=True)
    choice = st.selectbox("Select Structure:", ["Steroid Nucleus", "Phenothiazine", "Imidazole", "Beta-Lactam", "Benzene"])
    if choice == "Steroid Nucleus":
        st.info("**The Cheat:** 3 Rooms and a Parlor. Draw 3 hexagons in a staircase and 1 pentagon at the end.")
    elif choice == "Phenothiazine":
        st.info("**The Cheat:** The Butterfly. 3 rings. 'S' on top, 'N' on bottom.")
    elif choice == "Imidazole":
        st.info("**The Cheat:** 5-sided house. 'N' at position 1 and 3.")
    elif choice == "Beta-Lactam":
        st.info("**The Cheat:** The Magic Square. 4-membered ring.")
    elif choice == "Benzene":
        st.latex(r"C_6H_6")
        st.info("**The Cheat:** Hexagon with a circle.")

# --- 6. LEADERBOARD ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Agulu Leaderboard</p>', unsafe_allow_html=True)
    nick = st.text_input("Nickname:")
    if st.button("Save Score"):
        new_row = pd.DataFrame([[nick, st.session_state.daily_score, "Senior Man"]], columns=['Name', 'Score', 'Status'])
        st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_row], ignore_index=True)
    st.table(st.session_state.leaderboard)

elif app_mode == "Marketplace":
    st.title("🛒 Marketplace")
    st.write("Coming soon.")

st.sidebar.divider()
st.sidebar.caption(f"Ayo's Desprix Crew ®2026")
            
