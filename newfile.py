import streamlit as st
import google.generativeai as genai
import time
import pandas as pd

# 1. Setup & API Config
# Ensure GEMINI_API_KEY is in your Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Set page config
st.set_page_config(page_title="Med AI", page_icon="🌿", layout="centered")

# --- CSS: PREMIUM DARK UI, TYPEWRITER, FALLING LEAVES & CUSTOM MENU ---
st.markdown("""
    <style>
    /* Overall Dark Theme (Rich Zinc/Slate) */
    [data-testid="stAppViewContainer"] {
        background-color: #09090b; /* Deep dark background */
        color: #fafafa;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #121214;
        border-right: 1px solid #27272a;
    }

    /* Pill-Shaped Buttons */
    .stButton>button {
        width: 100%; 
        border-radius: 25px; /* Pill shape */
        height: 3.2em;
        background-color: #18181b; /* Dark elevated card color */
        color: #e4e4e7; 
        font-weight: 500;
        border: 1px solid #27272a; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #27272a; 
        transform: translateY(-2px); 
        border-color: #3f3f46;
        color: #ffffff;
    }

    /* Primary/Submit Button override */
    .stButton>button[kind="primary"] {
        background-color: #2563eb; /* Vibrant Blue Accent */
        color: white;
        border: none;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #1d4ed8;
    }

    /* Top Right 3-Dot Menu Icon */
    .app-menu-icon {
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 28px;
        color: #a1a1aa;
        cursor: pointer;
        user-select: none;
        transition: color 0.2s;
    }
    .app-menu-icon:hover {
        color: #fafafa;
    }

    /* The Typewriter Effect */
    .typewriter {
        display: inline-block;
    }
    .typewriter h1 {
        overflow: hidden;
        border-right: .15em solid #10b981; /* Green cursor */
        white-space: nowrap;
        margin: 0 auto;
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: .05em;
        animation: 
            typing 1.5s steps(30, end),
            blink-caret .75s step-end infinite;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #10b981; } }

    /* Bubbling/Falling Leaves Animation (Dark Mode Adjusted) */
    .leaf {
        position: fixed;
        top: -10%;
        z-index: 9999;
        user-select: none;
        pointer-events: none;
        animation: fall linear infinite;
        font-size: 20px;
        opacity: 0.5; /* Slightly more transparent for dark mode */
        filter: drop-shadow(0px 0px 2px rgba(16, 185, 129, 0.4)); /* Subtle green glow */
    }
    @keyframes fall {
        0% { transform: translate(0, 0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.6; }
        90% { opacity: 0.6; }
        100% { transform: translate(100px, 100vh) rotate(360deg); opacity: 0; }
    }
    /* Individual leaf timings and positions */
    .l1 { left: 10%; animation-duration: 12s; animation-delay: 0s; }
    .l2 { left: 35%; animation-duration: 15s; animation-delay: 3s; font-size: 24px; }
    .l3 { left: 60%; animation-duration: 11s; animation-delay: 7s; }
    .l4 { left: 85%; animation-duration: 14s; animation-delay: 2s; font-size: 18px; }
    .l5 { left: 50%; animation-duration: 13s; animation-delay: 5s; }
    
    .pro-header {
        color: #60a5fa; font-size: 28px; font-weight: 700;
        text-align: left; margin-bottom: 20px;
    }
    
    /* Input field dark mode overrides */
    .stTextInput input, .stChatInput textarea {
        background-color: #18181b !important;
        color: #fafafa !important;
        border: 1px solid #27272a !important;
    }
    </style>
    
    <div class="leaf l1">🍃</div>
    <div class="leaf l2">🌿</div>
    <div class="leaf l3">🍃</div>
    <div class="leaf l4">🌿</div>
    <div class="leaf l5">🍃</div>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'daily_score' not in st.session_state: st.session_state.daily_score = 0
if 'leaderboard' not in st.session_state: 
    st.session_state.leaderboard = pd.DataFrame(columns=['Name', 'Score', 'Status'])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🌿 Desprix 2.5")
app_mode = st.sidebar.radio("Navigation:", 
    ["Home", "Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Exam Mastery Hub", "Structure Master Class", "Leaderboard"])

# --- 0. HOME (Dark App UI) ---
if app_mode == "Home":
    # The custom 3-dot menu at the top right
    st.markdown('<div class="app-menu-icon">⋮</div>', unsafe_allow_html=True)
    
    st.markdown('<br><br>', unsafe_allow_html=True)
    
    # Glowing Orb
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="width: 90px; height: 90px; background: radial-gradient(circle, #3b82f6, #1d4ed8); border-radius: 50%; box-shadow: 0 0 30px rgba(59, 130, 246, 0.6); display: flex; align-items: center; justify-content: center; font-size: 45px; color: white;">
                ✨
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Typewriter Greeting
    st.markdown("""
        <div style="text-align: center;">
            <div class="typewriter">
                <h1>HELLO</h1>
            </div>
            <p style="color: #a1a1aa; font-size: 18px; margin-top: 10px;">I'm Sina. How can I help you today?</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

    # Pill Suggestion Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button("✨ Verify a NAFDAC Number")
        st.button("✨ Explain a Drug Mechanism")
        st.button("✨ Help me with CBT Prep")

    # Bottom Chat Input Simulation
    st.markdown('<br><br>', unsafe_allow_html=True)
    user_query = st.chat_input("Ask me anything about medicine...")
    if user_query:
        st.info(f"You asked: {user_query} (Connect this to your Gemini routing!)")

# --- 1. FIND REMEDY ---
elif app_mode == "Find Remedy":
    st.markdown('<p class="pro-header">🌿 Herbal Remedy Guide</p>', unsafe_allow_html=True)
    u_input = st.text_input("What is the symptom?", placeholder="e.g. Fever, Malaria")
    if st.button("Search Remedy", type="primary"):
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            resp = model.generate_content(f"Pharmacist: Remedy for {u_input} with Pidgin summary.")
            st.markdown(resp.text)
        except Exception as e: st.error(f"Error: {e}")

# --- 2. DRUG RESEARCHER (PRO) ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & API</p>', unsafe_allow_html=True)
    drug = st.text_input("Enter Drug Name:")
    if st.button("Analyze API", type="primary"):
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"Pharmacologist: Deep breakdown of {drug} (API, Mechanism, Generics, Side effects)."
        resp = model.generate_content(prompt)
        st.success(resp.text)

# --- 3. NAFDAC VERIFIER ---
elif app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    reg = st.text_input("Enter NAFDAC Reg No:")
    if st.button("Verify Registration", type="primary"):
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash', tools=[{"google_search": {}}])
            resp = model.generate_content(f"Verify NAFDAC registration: {reg}. Name product and manufacturer.")
            st.info(resp.text)
        except Exception as e: st.error(f"Search Error: {e}")

# --- 4. EXAM MASTERY HUB ---
elif app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Daily Quiz", "🎤 Lecture Analyst", "📝 Note-to-CBT"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        st.write("Question: Which drug class inhibits cell wall synthesis?")
        ans = st.radio("Pick:", ["NSAIDs", "Penicillins", "Statins"])
        if st.button("Submit", type="primary"):
            if ans == "Penicillins": st.success("Correct!")
            else: st.error("Wrong!")

# --- 5. STRUCTURE MASTER CLASS ---
elif app_mode == "Structure Master Class":
    st.markdown('<p class="pro-header">🎨 Structure Cheats</p>', unsafe_allow_html=True)
    choice = st.selectbox("Select Structure:", ["Steroid Nucleus", "Phenothiazine", "Imidazole", "Beta-Lactam", "Benzene"])
    if choice == "Steroid Nucleus":
        st.info("**The Cheat:** 3 Rooms and a Parlor. Draw 3 hexagons in a staircase and 1 pentagon at the end.")
    elif choice == "Benzene":
        st.latex(r"C_6H_6")
        st.info("**The Cheat:** Hexagon with a circle.")

# --- 6. LEADERBOARD ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Agulu Leaderboard</p>', unsafe_allow_html=True)
    nick = st.text_input("Nickname:")
    if st.button("Save Score", type="primary"):
        new_row = pd.DataFrame([[nick, st.session_state.daily_score, "Senior Man"]], columns=['Name', 'Score', 'Status'])
        st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_row], ignore_index=True)
    st.table(st.session_state.leaderboard)

st.sidebar.divider()
st.sidebar.caption(f"Ayo's Desprix Crew ®2026")
        
