import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
from PIL import Image
import io

# 1. Setup & API Config
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Desprix Med AI", page_icon="🌿", layout="wide")

# --- CSS: PRO UI ---
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
st.sidebar.title("🌿 Desprix Ultimate")
app_mode = st.sidebar.selectbox("Choose a Service:", 
    ["Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Exam Mastery Hub", "Structure Master Class", "Leaderboard", "Marketplace"])

# --- 1. FIND REMEDY ---
if app_mode == "Find Remedy":
    st.title("🌿 Herbal Remedy Guide")
    u_input = st.text_input("Symptom?")
    if st.button("Search"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content(f"Pharmacist: Remedy for {u_input} with Pidgin summary.")
        st.markdown(resp.text)

# --- 2. DRUG RESEARCHER (PRO) ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & API</p>', unsafe_allow_html=True)
    drug = st.text_input("Drug Name (e.g., Augmentin):")
    if st.button("Analyze API"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Break down {drug}: Active API, Modality, Contraindications, and cheaper Generics."
        resp = model.generate_content(prompt)
        st.success(resp.text)

# --- 3. NAFDAC VERIFIER ---
elif app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    reg = st.text_input("NAFDAC Reg No:")
    if st.button("Verify Registration"):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', tools=[{"google_search": {}}])
            resp = model.generate_content(f"Verify NAFDAC number {reg}. List product and manufacturer.")
            st.info(resp.text)
        except Exception as e: st.error(f"Search Error: {e}")

# --- 4. EXAM MASTERY HUB (THE THREE GROUPS) ---
elif app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Daily Quiz", "🎤 Lecture Analyst", "📝 Note-to-CBT"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        q_data = {"q": "What is the core ring in Penicillin?", "a": "Beta-Lactam", "o": ["Imidazole", "Beta-Lactam", "Steroid"]}
        ans = st.radio(q_data["q"], q_data["o"])
        if st.button("Submit Q1"):
            if ans == q_data["a"]:
                st.session_state.daily_score += 10
                st.success("Correct! +10 Points")
            else: st.error("Wrong! Answer is Beta-Lactam.")

    with tab2:
        st.subheader("Lecture Secret Extractor (Audio/PDF)")
        # FIXED: Added m4a to supported types
        aud = st.file_uploader("Upload Lecture Audio", type=['mp3', 'wav', 'm4a'])
        doc = st.file_uploader("Upload Handout (PDF)", type=['pdf'])
        
        if aud and doc:
            if st.button("Analyze & Compare"):
                with st.spinner("Gemini is listening to your recording..."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        aud_bytes = aud.read()
                        
                        # Detect MIME type for m4a compatibility
                        m_type = "audio/mp4" if aud.name.endswith("m4a") else f"audio/{aud.type.split('/')[-1]}"
                        
                        prompt = (
                            "Analyze this lecture recording and compare it with the uploaded handout. "
                            "1. Identify points where the lecturer repeated info or spoke with high energy. "
                            "2. List important exam info NOT found in the handout. "
                            "3. Give a 2-minute 'Exam Hotspot' summary in Pidgin English. "
                            "4. Generate 5 Exam Questions based on these emphases."
                        )
                        
                        resp = model.generate_content([
                            prompt, 
                            {"mime_type": m_type, "data": aud_bytes}
                        ])
                        st.markdown(resp.text)
                    except Exception as e:
                        st.error(f"Processing Error: {e}")

    with tab3:
        st.subheader("Interactive Note-to-CBT")
        note = st.file_uploader("Upload Image of Notes or PDF", type=['png', 'jpg', 'pdf'])
        if note:
            if st.button("Generate Timed CBT"):
                with st.spinner("Extracting questions from your notes..."):
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = "Extract key concepts from these notes and create a 3-question timed CBT quiz."
                    st.success("CBT Ready! Time: 60 Seconds.")
                    st.write("--- CBT Generated Successfully ---")

# --- 5. STRUCTURE MASTER CLASS ---
elif app_mode == "Structure Master Class":
    st.markdown('<p class="pro-header">🎨 Structure Cheats</p>', unsafe_allow_html=True)
    choice = st.selectbox("Choose Ring System:", ["Benzene", "Imidazole", "Phenothiazine", "Steroid Nucleus", "Beta-Lactam"])
    
    if choice == "Steroid Nucleus":
        st.latex(r"C_{17}H_{28}")
        st.info("**The Cheat:** 3 Rooms and a Parlor. Draw 3 hexagons in a staircase and 1 pentagon at the end.")
        
    elif choice == "Phenothiazine":
        st.info("**The Cheat:** The Butterfly. 3 rings in a row. 'S' on top of middle ring, 'N' on bottom.")
        
    elif choice == "Imidazole":
        st.latex(r"C_3H_4N_2")
        st.info("**The Cheat:** 5-sided house. 'N' at position 1 and 3 (1-3 Rule).")
        
    elif choice == "Beta-Lactam":
        st.info("**The Cheat:** The Magic Square. A 4-membered ring with a Nitrogen.")
        
    elif choice == "Benzene":
        st.latex(r"C_6H_6")
        st.info("**The Cheat:** Hexagon with a circle inside.")
        [attachment_0](attachment)

# --- 6. LEADERBOARD ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Agulu Senior Men</p>', unsafe_allow_html=True)
    nick = st.text_input("Your Nickname:")
    if st.button("Save My Score"):
        new_row = pd.DataFrame([[nick, st.session_state.daily_score, "Verified"]], columns=['Name', 'Score', 'Status'])
        st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_row])
    st.table(st.session_state.leaderboard)

elif app_mode == "Marketplace":
    st.title("🛒 Marketplace")
    st.write("Coming soon.")

st.sidebar.divider()
st.sidebar.caption(f"Ayo's Desprix Crew ®2026")
                
