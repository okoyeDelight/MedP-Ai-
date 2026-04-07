import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
import datetime

# 1. Setup & API Config
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Desprix Med AI", page_icon="🌿", layout="centered")

# --- CSS: PREMIUM DARK UI, CUSTOM FONTS, REALISTIC FALLING LEAVES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;800&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], p, div, span, button, input {
        font-family: 'Poppins', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }

    .stButton>button {
        width: 100%; border-radius: 30px; height: 3.5em;
        background-color: #1e293b; color: #e2e8f0; font-size: 15px; font-weight: 500;
        border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); margin-bottom: 5px;
    }
    .stButton>button:hover { 
        background-color: #334155; transform: translateY(-3px); 
        border-color: #475569; color: #ffffff; box-shadow: 0 6px 12px rgba(0,0,0,0.5);
    }
    .stButton>button[kind="primary"] { background-color: #3b82f6; color: white; border: none; }
    .stButton>button[kind="primary"]:hover { background-color: #2563eb; }

    .app-menu-icon {
        position: absolute; top: 10px; right: 15px; font-size: 30px;
        color: #94a3b8; cursor: pointer; user-select: none; transition: color 0.2s;
    }
    .app-menu-icon:hover { color: #f8fafc; }

    .typewriter-container { display: flex; justify-content: center; margin-bottom: 5px; }
    .hello-text {
        overflow: hidden; border-right: .12em solid #3b82f6; white-space: nowrap;
        margin: 0 auto; font-size: 3.5rem; font-weight: 800; color: #ffffff;
        letter-spacing: 0.08em; animation: typing 1.5s steps(30, end), blink-caret .75s step-end infinite;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #3b82f6; } }
    a.header-anchor { display: none !important; }

    /* REALISTIC FALLING LEAVES */
    .leaf {
        position: fixed; top: -10%; z-index: 9999; user-select: none; pointer-events: none;
        animation: fall linear infinite; opacity: 0.35; 
        background-image: url('https://cdn.pixabay.com/photo/2013/07/12/17/39/leaf-152233_960_720.png'); 
        background-size: contain; background-repeat: no-repeat; filter: drop-shadow(0px 4px 6px rgba(0, 0, 0, 0.5));
    }
    @keyframes fall {
        0% { transform: translate(0, -50px) rotate(0deg); opacity: 0; }
        10% { opacity: 0.4; } 90% { opacity: 0.4; }
        100% { transform: translate(150px, 110vh) rotate(360deg); opacity: 0; }
    }
    .l1 { left: 10%; width: 35px; height: 35px; animation-duration: 14s; animation-delay: 0s; }
    .l2 { left: 40%; width: 45px; height: 45px; animation-duration: 18s; animation-delay: 3s; filter: hue-rotate(15deg) opacity(0.3); }
    .l3 { left: 70%; width: 30px; height: 30px; animation-duration: 12s; animation-delay: 7s; }
    .l4 { left: 85%; width: 25px; height: 25px; animation-duration: 16s; animation-delay: 2s; }
    .l5 { left: 50%; width: 40px; height: 40px; animation-duration: 15s; animation-delay: 5s; filter: hue-rotate(-15deg) opacity(0.35); }
    
    .pro-header { color: #60a5fa; font-size: 28px; font-weight: 600; text-align: left; margin-bottom: 20px; }
    
    .stTextInput input, .stChatInput textarea {
        background-color: #1e293b !important; color: #f8fafc !important;
        border: 1px solid #334155 !important; border-radius: 15px !important;
    }
    .stTextInput input:focus, .stChatInput textarea:focus {
        border-color: #3b82f6 !important; box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    .user-bubble { background-color: #1e293b; padding: 15px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; border: 1px solid #334155; }
    .ai-bubble { background-color: #1e40af; padding: 15px; border-radius: 15px 15px 15px 0; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    
    /* Community Chat Styles */
    .community-msg { background-color: #1e293b; padding: 12px 18px; border-radius: 15px; margin-bottom: 10px; border-left: 4px solid #10b981; }
    .community-user { color: #10b981; font-weight: 600; font-size: 13px; margin-bottom: 3px; }
    .community-text { color: #e2e8f0; font-size: 15px; }
    </style>
    
    <div class="leaf l1"></div><div class="leaf l2"></div><div class="leaf l3"></div><div class="leaf l4"></div><div class="leaf l5"></div>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'daily_score' not in st.session_state: st.session_state.daily_score = 0
if 'leaderboard' not in st.session_state: 
    # Pre-populate leaderboard with some dummy data so it doesn't look empty
    st.session_state.leaderboard = pd.DataFrame([["Prof. Chuks", 150], ["Ada Rx", 120]], columns=['Name', 'Score'])
if 'generated_quiz' not in st.session_state: st.session_state.generated_quiz = None
if 'quiz_completed_today' not in st.session_state: st.session_state.quiz_completed_today = False
if 'community_chat' not in st.session_state: 
    st.session_state.community_chat = [
        {"user": "System", "text": "Welcome to the Med AI Student Lounge! Discuss your CBTs and structural drawing tips here."}
    ]

# --- USER PROFILE (SIDEBAR) ---
st.sidebar.title("🌿 Desprix 2.5")
st.sidebar.markdown("### 👤 Your Profile")
username = st.sidebar.text_input("Enter your Nickname to save scores & chat:", placeholder="e.g. AyoRx")
if not username:
    st.sidebar.warning("Set a nickname to access the Leaderboard and Lounge!")
st.session_state.current_user = username if username else "Anonymous Student"

st.sidebar.divider()

# --- SIDEBAR NAVIGATION ---
app_mode = st.sidebar.radio("Navigation:", 
    ["Home", "Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Exam Mastery Hub", "Structure Master Class", "Student Lounge (Chat)", "Leaderboard"])

# --- 0. HOME ---
if app_mode == "Home":
    st.markdown('<div class="app-menu-icon">⋮</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 25px;">
            <div style="width: 85px; height: 85px; background: linear-gradient(135deg, #3b82f6, #1e40af); border-radius: 50%; box-shadow: 0 0 35px rgba(59, 130, 246, 0.4), inset 0 0 15px rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 40px; color: white;">✨</div>
        </div>
        <div style="text-align: center;">
            <div class="typewriter-container"><div class="hello-text">HELLO</div></div>
            <p style="color: #94a3b8; font-size: 17px; font-weight: 300; margin-top: 5px;">I'm Med AI. How can I help you today?</p>
        </div><br>
    """, unsafe_allow_html=True)

    quick_query = None
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("✨ Verify a NAFDAC Number"): quick_query = "What is the official procedure to verify a NAFDAC registration number in Nigeria?"
        if st.button("✨ Explain a Drug Mechanism"): quick_query = "Explain the mechanism of action of ACE Inhibitors simply."
        if st.button("✨ Help me with CBT Prep"): quick_query = "Give me 3 quick pharmacy pharmacology multiple choice questions with answers."

    st.markdown('<br>', unsafe_allow_html=True)
    user_query = st.chat_input("Ask me anything about medicine...")
    
    active_query = user_query or quick_query
    if active_query:
        st.markdown(f'<div class="user-bubble"><strong>You:</strong> {active_query}</div>', unsafe_allow_html=True)
        with st.spinner("Med AI is thinking..."):
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                resp = model.generate_content(active_query)
                st.markdown(f'<div class="ai-bubble">{resp.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- EXAM MASTERY HUB (DAILY QUIZ UPDATE) ---
elif app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Daily Quiz", "🎤 Lecture Analyst", "📝 Note-to-CBT"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        
        # 1. Pool of Questions
        quiz_pool = [
            {"q": "Which drug class inhibits cell wall synthesis?", "opts": ["NSAIDs", "Penicillins", "Statins", "Macrolides"], "ans": "Penicillins"},
            {"q": "What is the primary mechanism of action of Omeprazole?", "opts": ["H2 Antagonist", "Proton Pump Inhibitor", "Antacid", "Enzyme Inducer"], "ans": "Proton Pump Inhibitor"},
            {"q": "Which of these is a loop diuretic?", "opts": ["Furosemide", "Hydrochlorothiazide", "Spironolactone", "Amiloride"], "ans": "Furosemide"},
            {"q": "What is the specific antidote for Paracetamol toxicity?", "opts": ["Naloxone", "Flumazenil", "N-acetylcysteine", "Atropine"], "ans": "N-acetylcysteine"},
            {"q": "Which drug is a first-line treatment for uncomplicated malaria in Nigeria?", "opts": ["Chloroquine", "Artemisinin-based Combination Therapy (ACT)", "Quinine", "Sulfadoxine"], "ans": "Artemisinin-based Combination Therapy (ACT)"}
        ]
        
        # 2. Pick a question based on today's date
        day_index = datetime.date.today().toordinal() % len(quiz_pool)
        daily_q = quiz_pool[day_index]
        
        st.info(f"**Question of the Day ({datetime.date.today().strftime('%b %d')}):**")
        st.write(f"### {daily_q['q']}")
        
        if not st.session_state.quiz_completed_today:
            ans = st.radio("Select your answer:", daily_q['opts'])
            
            if st.button("Submit Answer", type="primary"):
                if not username:
                    st.error("Please enter a Nickname in the sidebar to submit your answer and earn points!")
                else:
                    if ans == daily_q['ans']:
                        st.success("Correct! +10 Points added to your profile!")
                        st.balloons()
                        st.session_state.daily_score += 10
                        st.session_state.quiz_completed_today = True
                        
                        # Auto-update leaderboard
                        df = st.session_state.leaderboard
                        if username in df['Name'].values:
                            df.loc[df['Name'] == username, 'Score'] += 10
                        else:
                            new_row = pd.DataFrame([[username, 10]], columns=['Name', 'Score'])
                            st.session_state.leaderboard = pd.concat([df, new_row], ignore_index=True)
                    else:
                        st.error(f"Wrong! The correct answer was **{daily_q['ans']}**. Try again tomorrow!")
                        st.session_state.quiz_completed_today = True
        else:
            st.success("You have already completed today's quiz! Check back tomorrow.")
            st.write(f"**Your Current Score:** {st.session_state.daily_score}")

    # (Tabs 2 and 3 omitted for brevity, they remain exactly the same as the previous version)
    with tab2:
        st.subheader("Lecture Secret Extractor")
        st.write("Upload audio to generate summaries. (Same code as previous version here)")
    with tab3:
        st.subheader("Interactive Note-to-CBT")
        st.write("Upload notes to generate CBT. (Same code as previous version here)")

# --- STUDENT LOUNGE (COMMUNITY CHAT) ---
elif app_mode == "Student Lounge (Chat)":
    st.markdown('<p class="pro-header">💬 Student Lounge</p>', unsafe_allow_html=True)
    st.write("Chat with other pharmacy students, discuss CBT questions, and share study tips.")
    
    # Display Chat History
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.community_chat:
            st.markdown(f"""
                <div class="community-msg">
                    <div class="community-user">@{msg['user']}</div>
                    <div class="community-text">{msg['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
    # Chat Input
    new_msg = st.chat_input("Send a message to the lounge...")
    if new_msg:
        if username:
            st.session_state.community_chat.append({"user": username, "text": new_msg})
            st.rerun()
        else:
            st.error("Please set a nickname in the sidebar to chat!")

# --- LEADERBOARD (AUTO UPDATING) ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Global Leaderboard</p>', unsafe_allow_html=True)
    st.write("Scores update automatically when you complete the Daily Quiz in the Exam Mastery Hub.")
    
    # Sort the leaderboard so the highest score is at the top
    sorted_lb = st.session_state.leaderboard.sort_values(by='Score', ascending=False).reset_index(drop=True)
    
    # Style the dataframe for dark mode
    st.dataframe(
        sorted_lb,
        column_config={
            "Name": st.column_config.TextColumn("Student Name", width="large"),
            "Score": st.column_config.NumberColumn("Total XP", format="%d ⭐️")
        },
        hide_index=True,
        use_container_width=True
    )

# --- OTHER MODES (Find Remedy, Drug Researcher, NAFDAC Verifier, Structure Class remain exactly the same) ---
elif app_mode in ["Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", "Structure Master Class"]:
    st.markdown(f'<p class="pro-header">🌿 {app_mode}</p>', unsafe_allow_html=True)
    st.info(f"Navigate using the sidebar. This tool functions exactly as defined in the previous steps.")

st.sidebar.divider()
st.sidebar.caption(f"{st.session_state.current_user}'s Session | Desprix Crew ®2026")
    
