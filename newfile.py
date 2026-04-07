import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
import os
import datetime

# --- MINI DATABASE SETUP ---
CHAT_DB = "global_chat.json"
LEADERBOARD_DB = "global_leaderboard.json"

def load_chat():
    if os.path.exists(CHAT_DB):
        try:
            with open(CHAT_DB, "r") as f:
                return json.load(f)
        except:
            return []
    return [{"user": "System", "text": "Welcome to the Med AI Student Lounge! Discuss your CBTs and structural drawing tips here."}]

def save_chat(chat_list):
    with open(CHAT_DB, "w") as f:
        json.dump(chat_list, f)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_DB):
        try:
            return pd.read_json(LEADERBOARD_DB)
        except:
            pass
    return pd.DataFrame([["Prof. Chuks", 150], ["Ada Rx", 120]], columns=['Name', 'Score'])

def save_leaderboard(df):
    df.to_json(LEADERBOARD_DB)

# 1. Setup & API Config
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit secrets.")

st.set_page_config(page_title="Desprix Med AI", page_icon="🌿", layout="centered")

# --- CSS: MOBILE-OPTIMIZED PREMIUM DARK UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;800&display=swap');

    p, h1, h2, h3, h4, h5, h6, div.stMarkdown, .stButton>button, .stTextInput input, .stChatInput textarea {
        font-family: 'Poppins', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }

    .stButton>button {
        width: 100%; border-radius: 25px; padding: 12px 10px;
        background-color: #1e293b; color: #e2e8f0; font-size: 14px; font-weight: 500;
        border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        transition: all 0.3s ease; margin-bottom: 8px;
    }
    .stButton>button:hover { 
        background-color: #334155; transform: translateY(-2px); 
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
        overflow: hidden; border-right: 3px solid #3b82f6; white-space: nowrap;
        margin: 0 auto; font-size: 2.8rem; font-weight: 800; color: #ffffff;
        letter-spacing: 0.08em; animation: typing 1.5s steps(30, end), blink-caret .75s step-end infinite;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #3b82f6; } }
    
    a.header-anchor { display: none !important; }

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
    
    .community-msg { background-color: #1e293b; padding: 12px 18px; border-radius: 15px; margin-bottom: 10px; border-left: 4px solid #10b981; }
    .community-user { color: #10b981; font-weight: 600; font-size: 13px; margin-bottom: 3px; }
    .community-text { color: #e2e8f0; font-size: 15px; }
    
    /* Highlight style for when a user is tagged */
    .tagged-msg {
        background-color: #27272a; 
        border-left: 4px solid #fbbf24; 
        box-shadow: 0 0 10px rgba(251, 191, 36, 0.2);
    }
    .tagged-text { color: #fbbf24; font-weight: bold; }
    </style>
    
    <div class="leaf l1"></div><div class="leaf l2"></div><div class="leaf l3"></div><div class="leaf l4"></div><div class="leaf l5"></div>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'daily_score' not in st.session_state: st.session_state.daily_score = 0
if 'generated_quiz' not in st.session_state: st.session_state.generated_quiz = None
if 'quiz_completed_today' not in st.session_state: st.session_state.quiz_completed_today = False

# --- PRE-LOAD CHAT FOR NOTIFICATIONS ---
global_chat = load_chat()
total_messages = len(global_chat)

if 'last_seen_messages' not in st.session_state:
    st.session_state.last_seen_messages = total_messages

# Calculate unread messages
unread_count = total_messages - st.session_state.last_seen_messages
chat_nav_label = f"Student Lounge (Chat) 🔴 {unread_count}" if unread_count > 0 else "Student Lounge (Chat)"


# --- USER PROFILE (SIDEBAR) ---
st.sidebar.title("🌿 Desprix 2.5")
st.sidebar.markdown("### 👤 Your Profile")
username = st.sidebar.text_input("Enter your Nickname to save scores & chat:", placeholder="e.g. Ayo")
if not username:
    st.sidebar.warning("Set a nickname to access the Leaderboard and Lounge!")
st.session_state.current_user = username if username else "Anonymous Student"

st.sidebar.divider()

# --- SIDEBAR NAVIGATION ---
app_mode = st.sidebar.radio("Navigation:", 
    ["Home", "Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Exam Mastery Hub", "Structure Master Class", chat_nav_label, "Leaderboard"])

# --- 0. HOME ---
if app_mode == "Home":
    st.markdown('<div class="app-menu-icon">⋮</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="width: 75px; height: 75px; background: linear-gradient(135deg, #3b82f6, #1e40af); border-radius: 50%; box-shadow: 0 0 25px rgba(59, 130, 246, 0.4), inset 0 0 15px rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 35px; color: white;">✨</div>
        </div>
        <div style="text-align: center;">
            <div class="typewriter-container"><div class="hello-text">HELLO</div></div>
            <p style="color: #94a3b8; font-size: 16px; font-weight: 300; margin-top: 5px;">I'm Med AI. How can I help you today?</p>
        </div><br>
    """, unsafe_allow_html=True)

    quick_query = None
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("✨ Verify a NAFDAC Number"): quick_query = "What is the official procedure to verify a NAFDAC registration number in Nigeria?"
        if st.button("✨ Explain a Drug Mechanism"): quick_query = "Explain the mechanism of action of ACE Inhibitors using very simple terms, everyday analogies, and a little bit of Nigerian Pidgin."
        if st.button("✨ Help me with CBT Prep"): quick_query = "Give me 3 quick pharmacy pharmacology multiple choice questions with answers."

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    
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
                st.error(f"Connection Error: {e}. Check your API Key or Network.")

# --- 1. FIND REMEDY ---
elif app_mode == "Find Remedy":
    st.markdown('<p class="pro-header">🌿 Herbal Remedy Guide</p>', unsafe_allow_html=True)
    u_input = st.text_input("What is the symptom?", placeholder="e.g. Fever, Malaria")
    if st.button("Search Remedy", type="primary"):
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            prompt = f"Act as a friendly Nigerian pharmacist. Give a practical remedy for {u_input} in very simple English, and then provide a short, funny summary in Nigerian Pidgin."
            resp = model.generate_content(prompt)
            st.markdown(resp.text)
        except Exception as e: st.error(f"Error: {e}")

# --- 2. DRUG RESEARCHER (PRO) ---
elif app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & API</p>', unsafe_allow_html=True)
    drug = st.text_input("Enter Drug Name:")
    if st.button("Analyze API", type="primary"):
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"Pharmacologist: Deep breakdown of {drug} (API, Mechanism, Generics, Side effects). Explain it so a 200-level pharmacy student understands it perfectly."
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

# --- 4. EXAM MASTERY HUB (DAILY QUIZ & CBT MAKER) ---
elif app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Daily Quiz", "🎤 Lecture Analyst", "📝 Note-to-CBT"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        
        quiz_pool = [
            {"q": "Which drug class inhibits cell wall synthesis?", "opts": ["NSAIDs", "Penicillins", "Statins", "Macrolides"], "ans": "Penicillins"},
            {"q": "What is the primary mechanism of action of Omeprazole?", "opts": ["H2 Antagonist", "Proton Pump Inhibitor", "Antacid", "Enzyme Inducer"], "ans": "Proton Pump Inhibitor"},
            {"q": "Which of these is a loop diuretic?", "opts": ["Furosemide", "Hydrochlorothiazide", "Spironolactone", "Amiloride"], "ans": "Furosemide"},
            {"q": "What is the specific antidote for Paracetamol toxicity?", "opts": ["Naloxone", "Flumazenil", "N-acetylcysteine", "Atropine"], "ans": "N-acetylcysteine"},
            {"q": "Which drug is a first-line treatment for uncomplicated malaria in Nigeria?", "opts": ["Chloroquine", "Artemisinin-based Combination Therapy (ACT)", "Quinine", "Sulfadoxine"], "ans": "Artemisinin-based Combination Therapy (ACT)"}
        ]
        
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
                        
                        global_lb = load_leaderboard()
                        if username in global_lb['Name'].values:
                            global_lb.loc[global_lb['Name'] == username, 'Score'] += 10
                        else:
                            new_row = pd.DataFrame([[username, 10]], columns=['Name', 'Score'])
                            global_lb = pd.concat([global_lb, new_row], ignore_index=True)
                        save_leaderboard(global_lb)
                        
                    else:
                        st.error(f"Wrong! The correct answer was **{daily_q['ans']}**. Try again tomorrow!")
                        st.session_state.quiz_completed_today = True
        else:
            st.success("You have already completed today's quiz! Check back tomorrow.")
            st.write(f"**Your Current Score:** {st.session_state.daily_score} XP")

    with tab2:
        st.subheader("Lecture Secret Extractor")
        aud = st.file_uploader("Upload Lecture Audio", type=['mp3', 'wav', 'm4a'])
        doc = st.file_uploader("Upload Class Handout", type=['pdf'])
        if aud and doc:
            if st.button("Analyze & Compare", type="primary"):
                with st.spinner("Med AI is listening and reading..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        aud_bytes = aud.read()
                        m_type = "audio/mp4" if aud.name.endswith("m4a") else f"audio/{aud.type.split('/')[-1]}"
                        prompt = "Compare the audio to the handout. Find what the lecturer emphasized. Give a summary of the most important points in simple English, provide 3 likely exam questions, and end with a 'Street/Pidgin Summary' so the student never forgets it."
                        resp = model.generate_content([prompt, {"mime_type": m_type, "data": aud_bytes}])
                        st.markdown(resp.text)
                    except Exception as e: st.error(f"Error: {e}")

    with tab3:
        st.subheader("Interactive Note-to-CBT")
        note = st.file_uploader("Upload Notes (Image/PDF)", type=['png', 'jpg', 'pdf'])
        if note:
            if st.button("Generate Interactive CBT", type="primary"):
                with st.spinner("Extracting knowledge and building your quiz..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        mime_type = "application/pdf" if note.name.endswith('pdf') else f"image/{note.name.split('.')[-1]}"
                        prompt = """
                        Analyze this document and generate exactly 3 multiple-choice questions from the content. 
                        You MUST return ONLY a raw, valid JSON array. Do not include markdown blocks like ```json.
                        Format exactly like this:
                        [
                          {"question": "What is...", "options": ["A", "B", "C", "D"], "answer": "A"},
                          {"question": "How does...", "options": ["A", "B", "C", "D"], "answer": "C"}
                        ]
                        """
                        resp = model.generate_content([prompt, {"mime_type": mime_type, "data": note.read()}])
                        raw_json = resp.text.strip().removeprefix('```json').removesuffix('```').strip()
                        st.session_state.generated_quiz = json.loads(raw_json)
                        st.success("Quiz Generated! Scroll down to take it.")
                    except Exception as e:
                        st.error(f"Could not generate quiz. Make sure the file is readable. Details: {e}")

        if st.session_state.generated_quiz:
            st.markdown("---")
            st.markdown("### 📝 Your Custom CBT")
            for i, q in enumerate(st.session_state.generated_quiz):
                st.markdown(f"**Question {i+1}:** {q['question']}")
                user_ans = st.radio("Select an option:", q['options'], key=f"user_ans_{i}")
                with st.expander(f"Reveal Answer for Q{i+1}"):
                    if user_ans == q['answer']: st.success(f"**Correct!** The answer is {q['answer']}")
                    else: st.error(f"**Incorrect.** The correct answer is {q['answer']}")
            
            if st.button("Clear Quiz"):
                st.session_state.generated_quiz = None
                st.rerun()

# --- 5. STRUCTURE MASTER CLASS ---
elif app_mode == "Structure Master Class":
    st.markdown('<p class="pro-header">🎨 Dynamic Structure Cheats</p>', unsafe_allow_html=True)
    st.write("Search for any drug, nucleus, or chemical structure to learn the easiest way to draw it.")
    
    struct_query = st.text_input("Enter a structure (e.g., Penicillin, Steroid Nucleus, Paracetamol):", placeholder="Type a chemical name...")
    
    if st.button("Teach Me How To Draw This", type="primary"):
        if struct_query:
            with st.spinner(f"Analyzing how to draw {struct_query}..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    prompt = f"""
                    You are a brilliant but relatable Nigerian pharmacy student teaching a junior colleague how to draw '{struct_query}'.
                    
                    Format your response exactly like this:
                    **Introduction:** Briefly explain what this is simply.
                    **The Cheat:** Provide a highly visual, easy-to-remember mnemonic or step-by-step physical guide (like 'draw a house and attach a hexagon'). Use simple, everyday terms.
                    **Key Features:** List what they must not forget. Include one sentence of encouragement in Nigerian Pidgin at the end.
                    """
                    resp = model.generate_content(prompt)
                    
                    st.markdown(f"""
                        <div style="background-color: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; margin-top: 15px;">
                            {resp.text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error fetching structure guide: {e}")
else:
            st.warning("Please type a structure name first!")

# --- 6. STUDENT LOUNGE (LIVE CHAT) ---
# We check "in app_mode" because the label changes dynamically with the unread badge
elif "Student Lounge" in app_mode:
    # Reset unread messages badge since user is viewing the chat
    st.session_state.last_seen_messages = total_messages
    
    st.markdown('<p class="pro-header">💬 Student Lounge</p>', unsafe_allow_html=True)
    st.write("Chat with other pharmacy students globally! Tag users with @Nickname.")
    
    @st.fragment(run_every=3)
    def live_chat_feed():
        current_chat = load_chat()
        chat_container = st.container(height=400)
        with chat_container:
            for msg in current_chat:
                # Check if the current user was tagged
                user_tag = f"@{username}"
                is_tagged = username and user_tag.lower() in msg['text'].lower()
                
                css_class = "community-msg tagged-msg" if is_tagged else "community-msg"
                
                # Bold the tag in the text if it exists
                display_text = msg['text']
                if is_tagged:
                    display_text = display_text.replace(user_tag, f'<span class="tagged-text">{user_tag}</span>')
                
                st.markdown(f"""
                    <div class="{css_class}">
                        <div class="community-user">@{msg['user']}</div>
                        <div class="community-text">{display_text}</div>
                    </div>
                """, unsafe_allow_html=True)

    live_chat_feed()
            
    new_msg = st.chat_input("Type a message... Tag someone with @Nickname")
    
    if new_msg:
        if username:
            current_chat = load_chat()
            current_chat.append({"user": username, "text": new_msg})
            save_chat(current_chat)
            # Update seen messages immediately so the badge doesn't light up for our own message
            st.session_state.last_seen_messages = len(current_chat)
            st.rerun() 
        else:
            st.error("Please set a nickname in the sidebar to chat!")

# --- 7. LEADERBOARD ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Global Leaderboard</p>', unsafe_allow_html=True)
    st.write("Scores update automatically when you complete the Daily Quiz in the Exam Mastery Hub.")
    
    global_lb = load_leaderboard()
    sorted_lb = global_lb.sort_values(by='Score', ascending=False).reset_index(drop=True)
    
    st.dataframe(
        sorted_lb,
        column_config={
            "Name": st.column_config.TextColumn("Student Name", width="large"),
            "Score": st.column_config.NumberColumn("Total XP", format="%d ⭐️")
        },
        hide_index=True,
        use_container_width=True
    )

st.sidebar.divider()
st.sidebar.caption(f"{st.session_state.current_user}'s Session | Desprix Crew ®2026")
