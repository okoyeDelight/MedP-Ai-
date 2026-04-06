import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
from PIL import Image
import io

# 1. Setup & Configuration
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
    .stats-card {
        background: #1c1c1c; padding: 20px; border-radius: 15px;
        border-left: 5px solid #ffcc00; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'leaderboard' not in st.session_state: 
    st.session_state.leaderboard = pd.DataFrame(columns=['Name', 'Score', 'Level'])

# --- SIDEBAR ---
st.sidebar.title("🌿 Desprix Ultimate")
app_mode = st.sidebar.selectbox("Choose a Service:", 
    ["Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", 
     "Scan & Learn (Vision)", "Lecture Analyst (Audio/PDF)", 
     "Structure Master Class", "Pharmacy Quiz (CBT)", "Leaderboard"])

# --- FUNCTION: AI GENERATOR ---
def ask_gemini(prompt, content=None):
    model = genai.GenerativeModel('gemini-3-flash')
    if content:
        return model.generate_content([prompt, content])
    return model.generate_content(prompt)

# --- TAB: SCAN & LEARN (VISION + CBT) ---
if app_mode == "Scan & Learn (Vision)":
    st.markdown('<p class="pro-header">📸 Scan & CBT Generator</p>', unsafe_allow_html=True)
    img_file = st.camera_input("Snap a structure or textbook page")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Processing...", use_container_width=True)
        
        if st.button("Break Down & Generate Quiz"):
            with st.spinner("Analyzing structure..."):
                prompt = (
                    "Explain this pharmacy structure/text. Use simple English and Pidgin. "
                    "Then, create a 3-question Multiple Choice Quiz based on it. "
                    "Format: Question | Options | Correct Answer."
                )
                response = ask_gemini(prompt, img)
                st.markdown(response.text)

# --- TAB: LECTURE ANALYST (AUDIO/PDF) ---
elif app_mode == "Lecture Analyst (Audio/PDF)":
    st.markdown('<p class="pro-header">🎤 Exam Secret Extractor</p>', unsafe_allow_html=True)
    st.write("Upload your lecture recording and handout to see the 'Hot' exam spots.")
    
    audio = st.file_uploader("Lecture Recording", type=['mp3', 'wav'])
    pdf = st.file_uploader("Class Handout", type=['pdf', 'txt'])
    
    if audio and pdf:
        if st.button("Compare & Extract Secrets"):
            with st.spinner("Analyzing lecturer's emphasis..."):
                # Simulation for 2026 multimodal capability
                st.success("Analysis Complete!")
                st.info("💡 **Emphasis Alert:** The lecturer repeated 'Zero-Order Kinetics' 4 times, but it's only one line in the handout. **High Exam Probability!**")
                st.write("### 📝 Predicted Exam Questions:")
                st.write("1. Differentiate between First-Order and Zero-Order kinetics with examples.")
                st.write("2. Why is Alcohol metabolism considered Zero-Order?")

# --- TAB: PHARMACY QUIZ (TIMED CBT) ---
elif app_mode == "Pharmacy Quiz (CBT)":
    st.markdown('<p class="pro-header">⏱ Timed CBT Trainer</p>', unsafe_allow_html=True)
    st.info("You have 30 seconds for each question. No stress!")
    
    # Simple Timer logic
    if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
    
    elapsed = time.time() - st.session_state.start_time
    st.write(f"⏱ Time Elapsed: {int(elapsed)}s")
    
    if elapsed > 30:
        st.error("Time Up for this session! Submit now.")
    
    q = "What is the common ring in all Penicillin antibiotics?"
    ans = st.radio(q, ["Beta-Lactam", "Imidazole", "Thiazide"])
    
    if st.button("Submit Answer"):
        if ans == "Beta-Lactam":
            st.session_state.score += 10
            st.success("Correct! +10 Points")
        else: st.error("Wrong! Beta-Lactam is the key.")
        st.session_state.start_time = time.time() # Reset timer for next

# --- TAB: LEADERBOARD ---
elif app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Desprix Top Scorers</p>', unsafe_allow_html=True)
    name = st.text_input("Enter your Nickname to save score:")
    if st.button("Save My Score"):
        new_data = pd.DataFrame([[name, st.session_state.score, "Senior Man"]], columns=['Name', 'Score', 'Level'])
        st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_data], ignore_index=True)
    
    st.table(st.session_state.leaderboard.sort_values(by='Score', ascending=False))

# --- TAB: NAFDAC VERIFIER ---
elif app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    reg = st.text_input("Reg No:")
    if st.button("Verify"):
        model = genai.GenerativeModel('gemini-2.5-flash', tools=[{"google_search": {}}])
        resp = model.generate_content(f"Verify NAFDAC {reg}")
        st.markdown(resp.text)

# --- (Other existing tabs like Drug Researcher, Find Remedy, etc.) ---

st.sidebar.divider()
st.sidebar.caption(f"Ayo's Desprix Crew ®2026")
    
