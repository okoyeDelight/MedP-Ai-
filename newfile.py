import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
import os
import datetime
from datetime import timedelta
import base64

# --- MINI DATABASE SETUP ---
CHAT_DB = "global_chat.json"
USERS_DB = "users_db.json"
PENDING_PRODUCTS_DB = "pending_products.json"
APPROVED_PRODUCTS_DB = "approved_products.json"

# --- DATABASE LOADERS & SAVERS ---
def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f: return json.load(f)
        except: return default_data
    return default_data

def save_json(file_path, data):
    with open(file_path, "w") as f: json.dump(data, f)

def load_chat(): return load_json(CHAT_DB, [{"user": "System", "text": "Welcome to the Lounge!"}])
def save_chat(data): save_json(CHAT_DB, data)

def load_users():
    return load_json(USERS_DB, {
        "MED AI": {
            "password": "Desprix07!", "score": 100, "avatar": None,
            "bio": "Founder of Desprix", "school": "UNIZIK", 
            "level": "200L", "course": "Pharmacy", "phone": "08000000000",
            "saved_cbt": [], "saved_theory": []
        }
    })
    
def save_users(data): save_json(USERS_DB, data)

def load_pending_products(): return load_json(PENDING_PRODUCTS_DB, [])
def save_pending_products(data): save_json(PENDING_PRODUCTS_DB, data)

def load_approved_products(): 
    default_product = [{
        "name": "NaturCure Malaria Cleanser", 
        "treats": "Malaria, Fever", 
        "ingredients": "Artemisia annua, Neem",
        "contraindications": "Pregnancy",
        "dosage_form": "Liquid Syrup",
        "price": "₦2,500", 
        "dosage": "1 cap full morning and night", 
        "link": "https://wa.me/2340000000000",
        "vendor": "System Demo",
        "expiry_date": (datetime.datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "image": None
    }]
    return load_json(APPROVED_PRODUCTS_DB, default_product)
def save_approved_products(data): save_json(APPROVED_PRODUCTS_DB, data)

def log_user_history(username, action_detail):
    db = load_users()
    if username in db:
        timestamp = datetime.datetime.now().strftime("%b %d, %H:%M")
        db[username]["history"].insert(0, f"[{timestamp}] {action_detail}")
        db[username]["history"] = db[username]["history"][:20]
        save_users(db)

# 1. Setup & API Config
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit secrets.")

st.set_page_config(page_title="Desprix Med AI", page_icon="💊", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: ULTIMATE PREMIUM UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;800&display=swap');

    /* UI FIX: MAKE THE 3-LINE MENU BUTTON VISIBLE & BLUE */
    header[data-testid="stHeader"] {
        visibility: visible !important;
        display: block !important;
        background: rgba(0,0,0,0) !important;
    }

    button[kind="header"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.8) !important;
    }

    [data-testid="stAppViewContainer"] { background-color: #0b0f19; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }

    .stButton>button {
        width: 100%; border-radius: 25px; padding: 12px 10px;
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        color: #e2e8f0; font-size: 14px; font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); margin-bottom: 8px;
    }

    .hello-text { overflow: hidden; border-right: 3px solid #3b82f6; white-space: nowrap; margin: 0 auto; font-size: 2.5rem; font-weight: 800; color: white; width: 0; animation: typing 2s steps(20, end) forwards, blink-caret .75s step-end infinite; }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #3b82f6 } }

    .user-bubble { background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 14px 18px; border-radius: 20px 20px 5px 20px; color: white; margin-bottom: 10px; align-self: flex-end; box-shadow: 0 4px 15px rgba(0,0,0,0.2); max-width: 80%; }
    .ai-bubble { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); padding: 18px 22px; border-radius: 20px 20px 20px 5px; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); line-height: 1.6; }
    
    .glass-container { background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 20px; margin-bottom: 20px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem !important;}
</style>
""", unsafe_allow_html=True)


# --- INITIALIZE SESSION STATE ---
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'quiz_completed_today' not in st.session_state: st.session_state.quiz_completed_today = False
if 'active_quiz_answers' not in st.session_state: st.session_state.active_quiz_answers = {}

# --- PRE-LOAD CHAT FOR NOTIFICATIONS ---
global_chat = load_chat()
total_messages = len(global_chat)
if 'last_seen_messages' not in st.session_state: st.session_state.last_seen_messages = total_messages

# --- SIDEBAR & MAIN AUTHENTICATION SYSTEM ---
st.sidebar.title("🌿 Desprix 2.5")
users_db = load_users()

# CHECK FOR "REMEMBER ME" (Auto-login from URL)
query_params = st.query_params
if "user" in query_params and not st.session_state.get('logged_in_user'):
    saved_user = query_params["user"]
    if saved_user in users_db:
        st.session_state.logged_in_user = saved_user

# MAIN PAGE LOGIN (If not logged in)
if not st.session_state.get('logged_in_user'):
    st.markdown("<br><br>", unsafe_allow_html=True) 
    
    # This centers the login form
    col1, col2, col3 = st.columns([1, 2, 1]) 
    
    with col2:
        st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h2 style='color: #e2e8f0; font-weight: 600; margin-bottom: 5px;'>🔐 Secure Student Access</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 25px;'>Login or Sign Up to unlock Med AI features and save your progress.</p>", unsafe_allow_html=True)
        
        # Premium Tabs instead of radio buttons
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            login_user = st.text_input("Nickname", placeholder="Enter your nickname...", key="log_user")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password...", key="log_pass")
            login_remember = st.checkbox("Remember Me on this device", key="log_rem")
            
            if st.button("Log In", type="primary", use_container_width=True, key="log_btn"):
                if login_user and login_pass:
                    if login_user in users_db and users_db[login_user]["password"] == login_pass:
                        st.session_state.logged_in_user = login_user
                        if login_remember:
                            st.query_params["user"] = login_user
                        st.toast("Welcome back! 🚀")
                        st.rerun()
                    else:
                        st.error("Invalid Nickname or Password.")
                else:
                    st.warning("Please fill in both fields.")
                    
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            sign_user = st.text_input("Choose Nickname", placeholder="Enter a unique nickname...", key="sig_user")
            sign_pass = st.text_input("Create Password", type="password", placeholder="Create a secure password...", key="sig_pass")
            sign_remember = st.checkbox("Remember Me on this device", key="sig_rem")
            
            if st.button("Create Account", type="primary", use_container_width=True, key="sig_btn"):
                if sign_user and sign_pass:
                    if sign_user in users_db:
                        st.error("Nickname taken! Choose another or log in.")
                    else:
                        users_db[sign_user] = {"password": sign_pass, "score": 0, "history": [], "avatar": None, "saved_cbt": [], "saved_theory": []}
                        save_users(users_db)
                        st.session_state.logged_in_user = sign_user
                        if sign_remember:
                            st.query_params["user"] = sign_user
                        st.toast(f"Welcome {sign_user}! 🎉")
                        st.rerun()
                else:
                    st.warning("Please fill in both fields.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
                        
# --- USER IS LOGGED IN past this point ---
username = st.session_state.logged_in_user
user_data = users_db[username]

# Ensure lists exist for saved materials
if "saved_cbt" not in user_data: user_data["saved_cbt"] = []
if "saved_theory" not in user_data: user_data["saved_theory"] = []

st.sidebar.markdown(f"### 👤 Profile: @{username}")

# Profile Picture Logic
avatar_base64 = user_data.get("avatar")
if avatar_base64:
    st.sidebar.markdown(f'<img src="data:image/jpeg;base64,{avatar_base64}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #3b82f6; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto;">', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<div style="width: 80px; height: 80px; border-radius: 50%; background-color: #1e293b; display: flex; align-items: center; justify-content: center; border: 2px solid #3b82f6; margin-bottom: 10px; font-size: 30px; font-weight: bold; color: white; margin-left: auto; margin-right: auto;">{username[0].upper()}</div>', unsafe_allow_html=True)

pic_upload = st.sidebar.file_uploader("Change Picture", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

if pic_upload:
    # This button stops the "Rerun Loop" by making the save action manual
    if st.sidebar.button("💾 Confirm New Picture", use_container_width=True):
        encoded_img = base64.b64encode(pic_upload.read()).decode('utf-8')
        
        # Fresh load to stay in sync
        users_db = load_users()
        users_db[username]["avatar"] = encoded_img
        save_users(users_db)
        
        st.toast("Profile updated! 🌟")
        time.sleep(1)
        st.rerun()

st.sidebar.markdown(f"<div style='text-align: center;'><strong>XP:</strong> {user_data['score']} ⭐️</div>", unsafe_allow_html=True)

if st.sidebar.button("Log Out"):
    st.session_state.logged_in_user = None
    st.query_params.clear()
    st.rerun()

st.sidebar.divider()

# Calculate Chat Notifications
unread_count = total_messages - st.session_state.last_seen_messages
chat_nav_label = f"Student Lounge (Chat) 🔴 {unread_count}" if unread_count > 0 else "Student Lounge (Chat)"

nav_options = ["Home", "My Profile", "Find Remedy", "Drug Researcher (PRO)", "NAFDAC Verifier", "Exam Mastery Hub", "Structure Master Class", chat_nav_label, "Leaderboard", "🌿 Vendor Hub"]

if username == "MED AI":
    nav_options.append("👑 Admin Dashboard")

# THE GATEKEEPER: Unlocks the door for you
if username == "MED AI" and user_data.get('password') == "Desprix07!":
    modes.insert(0, "🛡️ Admin Dashboard")

app_mode = st.sidebar.selectbox("Navigate", nav_options)



                        # ==========================================
# APP SECTIONS
# ==========================================
# --- MY PROFILE SECTION ---
if app_mode == "My Profile":
    st.markdown('<p class="pro-header">👤 Student Profile</p>', unsafe_allow_html=True)
    with st.expander("📝 Edit My Details", expanded=True):
        new_bio = st.text_area("About Me", value=user_data.get("bio", ""), placeholder="e.g. Aspiring Pharmacist...")
        c1, c2 = st.columns(2)
        new_school = c1.text_input("University", value=user_data.get("school", "UNIZIK"))
        new_level = c2.selectbox("Level", ["100L", "200L", "300L", "400L", "500L", "600L"], index=1)
        new_course = st.text_input("Course", value=user_data.get("course", "Pharmacy"))
        new_phone = st.text_input("WhatsApp Number", value=user_data.get("phone", ""))
        
        if st.button("💾 Save Updates"):
            users_db[username].update({"bio":new_bio, "school":new_school, "level":new_level, "course":new_course, "phone":new_phone})
            save_users(users_db)
            st.toast("Profile Synced! ✅")
            st.rerun()

# --- 👑 ADMIN DASHBOARD ---
if app_mode == "👑 Admin Dashboard" and username == "MED AI":
    st.markdown('<p class="pro-header">👑 Admin Command Center</p>', unsafe_allow_html=True)
    admin_list = []
    for u, d in users_db.items():
        admin_list.append({
            "User": u, "Phone": d.get("phone"), "Level": d.get("level"), 
            "Course": d.get("course"), "School": d.get("school"), "XP": d.get("score")
        })
    st.table(admin_list)
    st.metric("Total Students", len(admin_list))
    st.divider()
    st.subheader("📦 Marketplace Approvals")
    pending_items = load_pending_products()
    
    if not pending_items:
        st.write("No pending items to approve.")
    else:
        for i, p in enumerate(pending_items):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{p['name']}** by @{p['vendor']} (₦{p['price']})")
            if col2.button("Approve ✅", key=f"appr_{i}"):
                live_db = load_approved_products()
                live_db.append(p)
                save_approved_products(live_db)
                
                # Remove from pending and refresh
                pending_items.pop(i)
                save_pending_products(pending_items)
                st.toast(f"Approved {p['name']}! 🚀")
                st.rerun()
                
# --- 0. HOME ---
if app_mode == "Home":
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
        if st.button("✨ Explain a Drug Mechanism"): quick_query = "Explain the mechanism of action of ACE Inhibitors simply."

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    user_query = st.chat_input("Ask me anything about medicine...")
    active_query = user_query or quick_query
    
    if active_query:
        log_user_history(username, f"Chatted: {active_query[:20]}...")
        st.markdown(f'<div style="display: flex; justify-content: flex-end;"><div class="user-bubble"><strong>You:</strong> {active_query}</div></div>', unsafe_allow_html=True)
        with st.spinner("Med AI is thinking..."):
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                resp = model.generate_content(active_query)
                st.markdown(f'<div class="ai-bubble">{resp.text}</div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"Connection Error: {e}")

# --- 1. FIND REMEDY ---
if app_mode == "Find Remedy":
    st.markdown('<p class="pro-header">🌿 Herbal Remedy Guide</p>', unsafe_allow_html=True)
    st.write("Get safe, step-by-step household remedies verified by AI.")
    u_input = st.text_input("What is your symptom or condition?", placeholder="e.g. Malaria, but I am 5 months pregnant")
    if st.button("Search Remedy", type="primary"):
        log_user_history(username, f"Searched Remedy: {u_input}")
        with st.spinner("Consulting Med AI..."):
            try:
                all_approved = load_approved_products()
                active_products = []
                today_date = datetime.datetime.now().strftime("%Y-%m-%d")
                for p in all_approved:
                    if p.get("expiry_date", "2000-01-01") >= today_date:
                        safe_prod = {k: v for k, v in p.items() if k != 'image'}
                        active_products.append(safe_prod)

                model = genai.GenerativeModel('models/gemini-2.5-flash')
                prompt = f"""
                Act as a strict, ethical Nigerian clinical pharmacist. Query: '{u_input}'
                1. Give a practical leaf remedy in simple English. Ensure it is safe based on the query.
                2. Provide a short, funny summary in Pidgin.
                3. VETTING: List of ACTIVE supplements: {json.dumps(active_products)}. 
                If a product is 100% safe for this context, recommend it under '🛒 Verified Supplements on Desprix Market'.
                """
                resp = model.generate_content(prompt)
                st.markdown(f'<div class="glass-container">{resp.text}</div>', unsafe_allow_html=True)
                
                for prod in all_approved:
                    if prod.get("expiry_date", "2000-01-01") >= today_date and prod['name'] in resp.text:
                        img_html = f'<img src="data:image/jpeg;base64,{prod["image"]}" style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 10px;">' if prod.get("image") else ""
                        st.markdown(f"""
                            <div style="background: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 15px; border: 1px solid rgba(16, 185, 129, 0.3); margin-top: 15px; text-align: center;">
                                {img_html}
                                <h3 style="margin-bottom: 5px; color: #10b981;">{prod['name']}</h3>
                                <p style="color: #cbd5e1; font-size: 14px;">{prod['dosage_form']} • {prod['price']}</p>
                                <a href="{prod['link']}" target="_blank" style="text-decoration: none;">
                                    <div style="background: linear-gradient(135deg, #10b981, #059669); padding: 10px; border-radius: 10px; color: white; font-weight: bold; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">🛒 Buy Now</div>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e: st.error(f"Error: {e}")

# --- 2. VENDOR HUB ---
if app_mode == "🌿 Vendor Hub":
    st.markdown('<p class="pro-header">🌿 Partner Marketplace</p>', unsafe_allow_html=True)
    
    tab_new, tab_dash = st.tabs(["➕ Submit New Product", "📊 My Dashboard"])
    
    with tab_new:
        st.write("List your verified herbal supplement on Desprix Med AI.")
        with st.form("vendor_application"):
            st.write("### 1. Product Details")
            prod_name = st.text_input("Product Name")
            prod_treats = st.text_input("What does it treat? (e.g. Malaria, Typhoid)")
            prod_img_upload = st.file_uploader("Upload Product Image (Required for display)", type=['png', 'jpg', 'jpeg'])
            
            st.write("### 2. Clinical Data (Hidden from Public)")
            prod_ingredients = st.text_area("Active Ingredients / Constituents")
            prod_contra = st.text_area("Contraindications & Interactions (Who must NOT take this?)")
            prod_dosage_form = st.text_input("Dosage Form (e.g. Liquid Syrup, Capsule)")
            prod_dosage = st.text_input("Dosage Instructions")
            
            st.write("### 3. Sales Info")
            prod_price = st.text_input("Selling Price to Customer (e.g. ₦2,500)")
            prod_link = st.text_input("WhatsApp Link or Website to Buy")
            
            st.write("### 4. Subscription Plan & Payment")
            st.info("🏦 Payment Details: Account Number: **1862690486** | Bank: **Access Bank**")
            plan_choice = st.radio("Select Listing Duration:", ["3 Months - ₦10,000", "6 Months - ₦18,000", "1 Year - ₦30,000"])
            pay_ref = st.text_input("Sender Name / Bank Transaction Reference")
            receipt_upload = st.file_uploader("Upload Payment Receipt", type=['png', 'jpg', 'jpeg'])

            submitted = st.form_submit_button("Submit Product & Payment for Approval", type="primary")
            if submitted:
                if prod_name and prod_treats and prod_ingredients and prod_contra and prod_link and pay_ref and prod_img_upload:
                    prod_img_base64 = base64.b64encode(prod_img_upload.read()).decode('utf-8')
                    receipt_base64 = base64.b64encode(receipt_upload.read()).decode('utf-8') if receipt_upload else None
                    days_to_add = 90 if "3 Months" in plan_choice else (180 if "6 Months" in plan_choice else 365)

                    pending = load_pending_products()
                    pending.append({
                        "type": "new_product", "name": prod_name, "treats": prod_treats, 
                        "ingredients": prod_ingredients, "contraindications": prod_contra,
                        "dosage_form": prod_dosage_form, "dosage": prod_dosage, 
                        "price": prod_price, "link": prod_link, "vendor": username,
                        "plan": plan_choice, "duration_days": days_to_add,
                        "payment_ref": pay_ref, "receipt": receipt_base64, "image": prod_img_base64
                    })
                    save_pending_products(pending)
                    st.success("✅ Application submitted! Admin will verify and activate your product.")
                    st.balloons()
                else:
                    st.error("Please fill in all fields and upload a product image.")

    with tab_dash:
        st.write("### Manage My Products")
        all_approved = load_approved_products()
        my_products = [p for p in all_approved if p.get("vendor") == username]
        
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if not my_products:
            st.info("You don't have any approved products yet.")
        else:
            for i, prod in enumerate(my_products):
                is_active = prod.get("expiry_date", "2000-01-01") >= today_date
                
                with st.container():
                    st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 15px; border: 1px solid {'#10b981' if is_active else '#ef4444'}; margin-bottom: 15px;">
                            <h4 style="margin:0;">{prod['name']}</h4>
                            <p style="margin: 5px 0; color: {'#10b981' if is_active else '#ef4444'}; font-weight: bold;">
                                Status: {'🟢 ACTIVE (Expires: ' + prod['expiry_date'] + ')' if is_active else '🔴 EXPIRED'}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if not is_active:
                        with st.expander(f"🔄 Renew Subscription for {prod['name']}"):
                            st.info("🏦 Payment Details: Account Number: **1862690486** | Bank: **Access Bank**")
                            r_plan = st.radio("Select Renewal Plan:", ["3 Months - ₦10,000", "6 Months - ₦18,000", "1 Year - ₦30,000"], key=f"r_plan_{i}")
                            r_ref = st.text_input("Payment Reference", key=f"r_ref_{i}")
                            r_receipt = st.file_uploader("Upload Receipt", type=['png', 'jpg'], key=f"r_rec_{i}")
                            
                            if st.button("Submit Renewal", key=f"r_btn_{i}", type="primary"):
                                if r_ref:
                                    r_days = 90 if "3 Months" in r_plan else (180 if "6 Months" in r_plan else 365)
                                    r_receipt_b64 = base64.b64encode(r_receipt.read()).decode('utf-8') if r_receipt else None
                                    
                                    pending = load_pending_products()
                                    pending.append({
                                        "type": "renewal", "name": prod['name'], "vendor": username,
                                        "plan": r_plan, "duration_days": r_days,
                                        "payment_ref": r_ref, "receipt": r_receipt_b64
                                    })
                                    save_pending_products(pending)
                                    st.success("Renewal payment submitted! Waiting for admin approval.")
                                else:
                                    st.error("Payment Reference is required.")

# --- 3. ADMIN DASHBOARD ---
if app_mode == "👑 Admin Dashboard" and username == "AdminAyo":
    st.markdown('<p class="pro-header">👑 Admin Dashboard</p>', unsafe_allow_html=True)
    st.write("Verify payments, review products, and manage renewals.")
    
    pending = load_pending_products()
    approved = load_approved_products()
    
    if len(pending) == 0:
        st.info("No pending applications or renewals.")
    else:
        for i, req in enumerate(pending):
            req_type = req.get("type", "new_product")
            header = f"🔄 RENEWAL: {req['name']} (@{req['vendor']})" if req_type == "renewal" else f"🆕 NEW: {req['name']} (@{req['vendor']})"
            
            with st.expander(header):
                st.markdown("<div style='background-color: rgba(251, 191, 36, 0.1); padding: 10px; border-left: 4px solid #fbbf24; border-radius: 5px;'>", unsafe_allow_html=True)
                st.write(f"💰 **Plan:** {req.get('plan')}")
                st.write(f"**Ref:** {req.get('payment_ref')}")
                if req.get('receipt'): st.image(base64.b64decode(req['receipt']), width=200)
                st.markdown("</div><br>", unsafe_allow_html=True)

                if req_type == "new_product":
                    if req.get('image'): st.image(base64.b64decode(req['image']), width=150)
                    st.write(f"**Treats:** {req['treats']}")
                    st.write(f"**Ingredients:** {req['ingredients']}")
                    st.write(f"**Contraindications:** {req['contraindications']}")

                col1, col2 = st.columns(2)
                if col1.button("✅ Verify & Approve", key=f"app_{i}"):
                    days = req.get('duration_days', 90)
                    new_expiry = (datetime.datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                    
                    if req_type == "new_product":
                        req['expiry_date'] = new_expiry
                        approved.append(req)
                    elif req_type == "renewal":
                        for p in approved:
                            if p['name'] == req['name'] and p['vendor'] == req['vendor']:
                                p['expiry_date'] = new_expiry
                    
                    save_approved_products(approved)
                    pending.pop(i)
                    save_pending_products(pending)
                    st.toast(f"Approved! Expiry set to {new_expiry}", icon="✅")
                    st.rerun()
                    
                if col2.button("❌ Reject", key=f"rej_{i}"):
                    pending.pop(i)
                    save_pending_products(pending)
                    st.toast("Request Rejected.", icon="❌")
                    st.rerun()

    st.divider()
    st.write("### Currently Active Products")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    for prod in approved:
        status = "🟢 Active" if prod.get('expiry_date', '2000-01-01') >= today else "🔴 Expired"
        st.write(f"- {status}: **{prod['name']}** (Expires: {prod.get('expiry_date', 'N/A')}) | Vendor: @{prod.get('vendor')}")

# --- 4. DRUG RESEARCHER & 5. NAFDAC ---
if app_mode == "Drug Researcher (PRO)":
    st.markdown('<p class="pro-header">🧪 Drug Research & API</p>', unsafe_allow_html=True)
    drug = st.text_input("Enter Drug Name:")
    if st.button("Analyze API", type="primary"):
        log_user_history(username, f"Analyzed Drug: {drug}")
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        resp = model.generate_content(f"Deep breakdown of {drug} for pharmacy student.")
        st.markdown(f'<div class="glass-container">{resp.text}</div>', unsafe_allow_html=True)

if app_mode == "NAFDAC Verifier":
    st.markdown('<p class="pro-header">🔍 Live NAFDAC Verifier</p>', unsafe_allow_html=True)
    reg = st.text_input("Enter NAFDAC Reg No:")
    if st.button("Verify Registration", type="primary"):
        log_user_history(username, f"Verified NAFDAC: {reg}")
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash', tools=[{"google_search": {}}])
            resp = model.generate_content(f"Verify NAFDAC registration: {reg}.")
            st.markdown(f'<div class="glass-container">{resp.text}</div>', unsafe_allow_html=True)
        except Exception as e: st.error("Search Error")

# --- 6. EXAM MASTERY HUB (MASSIVELY UPGRADED) ---
if app_mode == "Exam Mastery Hub":
    st.markdown('<p class="pro-header">🎓 Exam Mastery Hub</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Daily Quiz", "🎤 Audio Analyst", "📝 Note-to-CBT", "✍️ Note-to-Theory", "📂 Saved Materials"])

    with tab1:
        st.subheader("Daily Pharmacy CBT Drill")
        quiz_pool = [
            {"q": "Which drug class inhibits cell wall synthesis?", "opts": ["NSAIDs", "Penicillins", "Statins", "Macrolides"], "ans": "Penicillins"},
            {"q": "What is the primary mechanism of action of Omeprazole?", "opts": ["H2 Antagonist", "Proton Pump Inhibitor", "Antacid", "Enzyme Inducer"], "ans": "Proton Pump Inhibitor"},
            {"q": "Which of these is a loop diuretic?", "opts": ["Furosemide", "Hydrochlorothiazide", "Spironolactone", "Amiloride"], "ans": "Furosemide"},
            {"q": "What is the specific antidote for Paracetamol toxicity?", "opts": ["Naloxone", "Flumazenil", "N-acetylcysteine", "Atropine"], "ans": "N-acetylcysteine"},
            {"q": "Which drug is a first-line treatment for uncomplicated malaria in Nigeria?", "opts": ["Chloroquine", "Artemisinin-based Combination Therapy (ACT)", "Quinine", "Sulfadoxine"], "ans": "Artemisinin-based Combination Therapy (ACT)"},
            {"q": "What is the most common side effect of ACE inhibitors like Lisinopril?", "opts": ["Dry cough", "Weight gain", "Insomnia", "Tachycardia"], "ans": "Dry cough"},
            {"q": "Which vitamin deficiency causes scurvy?", "opts": ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D"], "ans": "Vitamin C"}
        ]
        day_index = datetime.date.today().toordinal() % len(quiz_pool)
        daily_q = quiz_pool[day_index]
        
        st.info(f"**Question of the Day ({datetime.date.today().strftime('%b %d')}):**")
        st.write(f"### {daily_q['q']}")
        
        if not st.session_state.quiz_completed_today:
            ans = st.radio("Select your answer:", daily_q['opts'])
            if st.button("Check Answer", type="primary"):
                if ans == daily_q['ans']:
                    st.success("✅ Correct! +10 XP")
                    st.session_state.quiz_completed_today = True
                    users_db = load_users()
                    users_db[username]["score"] += 10
                    save_users(users_db)
                    st.rerun()
                else:
                    st.error(f"❌ Wrong! The correct answer was {daily_q['ans']}.")
                    st.session_state.quiz_completed_today = True
        else:
            st.success("You have already completed today's quiz!")

    with tab2:
        st.subheader("Lecture Secret Extractor")
        aud = st.file_uploader("Upload Lecture Audio", type=['mp3', 'wav', 'm4a'])
        doc = st.file_uploader("Upload Class Handout", type=['pdf'])
        if aud and doc:
            if st.button("Analyze Audio & Compare", type="primary"):
                log_user_history(username, "Used Lecture Analyst")
                with st.spinner("Med AI is listening..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        m_type = "audio/mp4" if aud.name.endswith("m4a") else f"audio/{aud.type.split('/')[-1]}"
                        resp = model.generate_content(["Compare audio to handout and summarize main points.", {"mime_type": m_type, "data": aud.read()}])
                        st.markdown(f'<div class="glass-container">{resp.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error("Error reading files.")

    with tab3:
        st.subheader("Interactive Note-to-CBT (Auto-Saves)")
        cbt_note = st.file_uploader("Upload Notes for MCQs", type=['png', 'jpg', 'pdf'])
        quiz_title = st.text_input("Name this Quiz (e.g., Pharm 201 Midterm):")
        if cbt_note and quiz_title:
            if st.button("Generate & Save CBT", type="primary"):
                log_user_history(username, f"Generated CBT: {quiz_title}")
                with st.spinner("Building your quiz..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        mime_type = "application/pdf" if cbt_note.name.endswith('pdf') else f"image/{cbt_note.name.split('.')[-1]}"
                        prompt = "Analyze this document and generate exactly 4 multiple-choice questions. Return ONLY a raw JSON array: [{'question': '...', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}]."
                        resp = model.generate_content([prompt, {"mime_type": mime_type, "data": cbt_note.read()}])
                        raw_json = resp.text.strip().removeprefix('```json').removesuffix('```').strip()
                        new_quiz = json.loads(raw_json)
                        
                        users_db = load_users()
                        quiz_entry = {
                            "id": str(int(time.time())), 
                            "title": quiz_title, 
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"), 
                            "questions": new_quiz
                        }
                        users_db[username]["saved_cbt"].insert(0, quiz_entry)
                        save_users(users_db)
                        
                        st.toast("✅ CBT Generated and Saved to your Profile!")
                        st.rerun() 
                    except Exception as e: st.error(f"Error: {e}")

    with tab4:
        st.subheader("Note-to-Theory (Essay Question Generator)")
        theory_note = st.file_uploader("Upload Notes for Theory Prep", type=['png', 'jpg', 'pdf'])
        theory_title = st.text_input("Name this Topic (e.g., Autonomic Nervous System):")
        if theory_note and theory_title:
            if st.button("Generate & Save Theory Exam", type="primary"):
                log_user_history(username, f"Generated Theory: {theory_title}")
                with st.spinner("Drafting standard essay questions & grading guides..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        mime_type = "application/pdf" if theory_note.name.endswith('pdf') else f"image/{theory_note.name.split('.')[-1]}"
                        prompt = "Based on this document, generate 3 standard university-level pharmacy essay/theory questions. Below each question, provide a 'Grading Guide' showing the key bullet points a lecturer would expect to see for full marks."
                        resp = model.generate_content([prompt, {"mime_type": mime_type, "data": theory_note.read()}])
                        
                        users_db = load_users()
                        theory_entry = {
                            "id": str(int(time.time())),
                            "title": theory_title,
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "content": resp.text
                        }
                        users_db[username]["saved_theory"].insert(0, theory_entry)
                        save_users(users_db)
                        
                        st.toast("✅ Theory Exam Generated and Saved!")
                        st.rerun()
                    except Exception as e: st.error("Error generating theory exam.")

    with tab5:
        st.subheader("📂 My Saved Materials")
        st.write("All your generated CBTs and Theory Exams stay here forever.")
        
        users_db = load_users()
        saved_cbts = users_db[username].get("saved_cbt", [])
        saved_theory = users_db[username].get("saved_theory", [])
        
        col_cbt, col_theory = st.columns(2)
        
        with col_cbt:
            st.markdown("#### 📝 Saved CBTs")
            if not saved_cbts: st.info("No saved CBTs.")
            for quiz in saved_cbts:
                with st.expander(f"Take: {quiz['title']} ({quiz['date']})"):
                    for i, q in enumerate(quiz['questions']):
                        st.markdown(f"**Q{i+1}:** {q['question']}")
                        ans_key = f"ans_{quiz['id']}_{i}"
                        user_ans = st.radio("Options:", q['options'], key=ans_key, label_visibility="collapsed")
                        
                        if st.button("Check Answer", key=f"btn_{quiz['id']}_{i}"):
                            if user_ans == q['answer']:
                                st.success("✅ Correct!")
                            else:
                                st.error(f"❌ Wrong! The correct answer is: **{q['answer']}**")
                    
        with col_theory:
            st.markdown("#### ✍️ Saved Theory Exams")
            if not saved_theory: st.info("No saved Theory exams.")
            for exam in saved_theory:
                with st.expander(f"Review: {exam['title']} ({exam['date']})"):
                    st.markdown(exam['content'])

# --- 7. STRUCTURE MASTER CLASS ---
if app_mode == "Structure Master Class":
    st.markdown('<p class="pro-header">🎨 Dynamic Structure Cheats</p>', unsafe_allow_html=True)
    struct_query = st.text_input("Enter a structure:", placeholder="Type a chemical name...")
    if st.button("Teach Me How To Draw This", type="primary"):
        if struct_query:
            log_user_history(username, f"Mastered Structure: {struct_query}")
            with st.spinner("Analyzing..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    resp = model.generate_content(f"Teach a pharmacy student how to draw '{struct_query}' using a visual mnemonic. Add Pidgin encouragement.")
                    st.markdown(f'<div class="glass-container">{resp.text}</div>', unsafe_allow_html=True)
                except Exception as e: st.error("Error.")

# --- 8. STUDENT LOUNGE (LIVE CHAT) ---
if "Student Lounge" in app_mode:
    st.session_state.last_seen_messages = total_messages
    st.markdown('<p class="pro-header">💬 Student Lounge</p>', unsafe_allow_html=True)
    
    @st.fragment(run_every=3)
    def live_chat_feed():
        current_chat = load_chat()
        all_users = load_users()
        chat_container = st.container(height=400)
        with chat_container:
            for msg in current_chat:
                sender = msg['user']
                sender_data = all_users.get(sender, {})
                sender_avatar = sender_data.get("avatar")
                avatar_html = f'<img src="data:image/jpeg;base64,{sender_avatar}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; margin-right: 8px; border: 1px solid #10b981;">' if sender_avatar else f'<div style="width: 28px; height: 28px; border-radius: 50%; background-color: #334155; display: flex; align-items: center; justify-content: center; margin-right: 8px; font-size: 14px; font-weight: bold; color: white;">{sender[0].upper()}</div>'
                is_tagged = username and f"@{username}".lower() in msg['text'].lower()
                css_class = "community-msg tagged-msg" if is_tagged else "community-msg"
                display_text = msg['text'].replace(f"@{username}", f'<span class="tagged-text">@{username}</span>') if is_tagged else msg['text']
                
                st.markdown(f"""
                    <div class="{css_class}">
                        <div style="display: flex; align-items: center; margin-bottom: 4px;">{avatar_html}<div class="community-user">@{sender}</div></div>
                        <div class="community-text">{display_text}</div>
                    </div>
                """, unsafe_allow_html=True)

    live_chat_feed()
    new_msg = st.chat_input("Type a message... Tag someone with @Nickname")
    if new_msg:
        current_chat = load_chat()
        current_chat.append({"user": username, "text": new_msg})
        save_chat(current_chat)
        st.session_state.last_seen_messages = len(current_chat)
        st.rerun() 

# --- 9. LEADERBOARD ---
if app_mode == "Leaderboard":
    st.markdown('<p class="pro-header">🏆 Global Leaderboard</p>', unsafe_allow_html=True)
    db = load_users()
    lb_data = [[user, data["score"]] for user, data in db.items()]
    global_lb = pd.DataFrame(lb_data, columns=['Name', 'Score']).sort_values(by='Score', ascending=False).reset_index(drop=True)
    st.dataframe(global_lb, hide_index=True, use_container_width=True)
# --- 🌿 VENDOR HUB (STUDENT MARKETPLACE) ---
if app_mode == "🌿 Vendor Hub":
    st.markdown('<p class="pro-header">🛍️ Student Marketplace</p>', unsafe_allow_html=True)
    
    st.warning("🛡️ **Safety Tip:** Always meet at a busy UNIZIK spot (like the Faculty entrance) to exchange items. Never pay before seeing the product!")

    tab1, tab2 = st.tabs(["🛒 Buy Items", "➕ Sell Something"])

    with tab1:
        approved_items = load_approved_products()
        if not approved_items:
            st.info("The market is empty. Be the first to list a textbook or lab coat!")
        else:
            for i, item in enumerate(approved_items):
                with st.container():
                    img_html = ""
                    if item.get("image"):
                        img_html = f'<img src="data:image/jpeg;base64,{item["image"]}" style="width:100%; border-radius:10px; margin-bottom:10px;">'

    st.markdown(f"""<div class="glass-container" style="margin-bottom: 15px; border: 1px solid #3b82f655; padding: 10px; border-radius: 12px;">
{img_html}
<h4 style="color: #3b82f6; margin-bottom: 5px;">{item['name']}</h4>
<p style="font-size: 1.2rem; font-weight: bold; color: #10b981; margin: 0;">₦{item['price']}</p>
<p style="font-size: 0.85rem; opacity: 0.8;"><b>Condition:</b> {item['dosage_form']} | <b>Seller:</b> @{item['vendor']}</p>
<p style="font-size: 0.9rem; margin-top: 5px;">{item['treats']}</p>
    </div>""", unsafe_allow_html=True)

    raw_phone = item.get('link', '').replace('+', '').replace(' ', '')
    if raw_phone.startswith('0'):
        wa_phone = "234" + raw_phone[1:]
    else:
        wa_phone = raw_phone
    msg = f"Hello, I am interested in your {item['name']} on Desprix Med AI."
    st.link_button(f"💬 Chat with @{item['vendor']}", f"https://api.whatsapp.com/send?phone={wa_phone}&text={msg}", use_container_width=True)
                            
                    
                
    with tab2:
        st.subheader("List Your Item")
        if not user_data.get('phone'):
            st.error("⚠️ You must add your phone number in **'My Profile'** before you can sell!")
        else:
            with st.form("market_form", clear_on_submit=True):
                item_name = st.text_input("Item Name (e.g. Lab Coat, 200L PQ)")
                price = st.text_input("Price (₦)")
                prod_pic = st.file_uploader("Upload Product Image", type=['png', 'jpg', 'jpeg'])
                condition = st.selectbox("Condition", ["Brand New", "Gently Used", "Well Used"])
                details = st.text_area("Description")
                
                if st.form_submit_button("🚀 Submit for Approval"):
                    if item_name and price:
                        img_str = None
                        if prod_pic:
                            img_str = base64.b64encode(prod_pic.read()).decode('utf-8')
                        
                        pending_db = load_pending_products()
                        pending_db.append({
                            "name": item_name, "price": price, "dosage_form": condition,
                            "treats": details, "vendor": username, 
                            "link": user_data.get('phone'), "image": img_str
                        })
                        save_pending_products(pending_db)
                        st.success("Sent to Admin for approval! ✅")
                        st.rerun()
# --- 🛡️ ADMIN DASHBOARD ---
if app_mode == "🛡️ Admin Dashboard":
    st.markdown('<p class="pro-header">🛡️ Admin Control Center</p>', unsafe_allow_html=True)
    pending_items = load_pending_products()
    
    if not pending_items:
        st.success("No items to approve. ✅")
    else:
        st.info(f"Reviewing {len(pending_items)} items...")
        for i, item in enumerate(pending_items):
            with st.container():
                st.write(f"**Item:** {item['name']} | **Price:** ₦{item['price']}")
                st.write(f"**Vendor:** @{item['vendor']} | **Details:** {item['treats']}")
                
                if st.button(f"✅ Approve {item['name']}", key=f"app_admin_{i}"):
                    # Move to Approved
                    approved = load_approved_products()
                    approved.append(item)
                    save_approved_products(approved)
                    # Remove from Pending
                    pending_items.pop(i)
                    save_pending_products(pending_items)
                    st.success("Item is now LIVE! 🚀")
                    st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"{username}'s Secured Session | Desprix Crew ©2026")
                
