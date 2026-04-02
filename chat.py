import streamlit as st
from supabase import create_client
import time

# --- 1. SETTINGS & LOGO ---
LOGO_URL = "https://img.icons8.com/ios-filled/512/FFFFFF/trident.png" 
AI_LINK = "https://veda-ultra-india.streamlit.app"

st.set_page_config(page_title="VibeLine", page_icon="🔱", layout="wide")

# --- 2. INITIALIZE SESSION STATE ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'view' not in st.session_state:
    st.session_state.view = "Chat"
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "them", "content": "Welcome to VibeLine ⚡"}]
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = "General Group"

# --- 3. SPLASH SCREEN ---
if not st.session_state.initialized:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            st.image(LOGO_URL, width=150)
            st.markdown("<h1 style='text-align: center; color: white;'>VibeLine</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>from</p>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #9d4edd;'>VEDA 3.0 ULTRA</h3>", unsafe_allow_html=True)
    time.sleep(3)
    placeholder.empty()
    st.session_state.initialized = True

# --- 4. CUSTOM CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; color: white; }}
    
    /* WhatsApp Bubbles */
    .chat-bubble-me {{ background-color: #005c4b; padding: 12px; border-radius: 15px 2px 15px 15px; margin: 8px; float: right; width: 75%; border: 1px solid #128c7e; color: white; }}
    .chat-bubble-them {{ background-color: #202c33; padding: 12px; border-radius: 2px 15px 15px 15px; margin: 8px; float: left; width: 75%; border: 1px solid #3b4a54; color: white; }}
    
    /* VEDA Button Styling */
    .veda-btn-container {{
        display: flex;
        align-items: center;
        background: rgba(157, 78, 237, 0.1);
        padding: 10px;
        border-radius: 50px;
        border: 1px solid #9d4edd;
        margin-bottom: 20px;
        text-align: center;
    }}
    
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #111b21; color: gray; font-size: 12px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    # This prevents the app from crashing if keys are missing
    supabase = None

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🔱 VibeLine")
    
    # Custom Meta-style VEDA button
    st.markdown('<div class="veda-btn-container"><div style="font-size:14px; width:100%;">🔱 Ask VEDA 3.0 ULTRA</div></div>', unsafe_allow_html=True)
    if st.button("Launch VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    st.caption("CHATS")
    chats = ["General Group", "Family", "Developers"]
    for chat in chats:
        if st.button(f"💬 {chat}", use_container_width=True):
            st.session_state.current_chat = chat
            st.session_state.view = "Chat"
            st.rerun()

# --- 7. MAIN CONTENT ---
if st.session_state.view == "Chat":
    st.subheader(f"⚡ {st.session_state.current_chat}")
    
    # Message Display
    for msg in st.session_state.messages:
        div_class = "chat-bubble-me" if msg["role"] == "me" else "chat-bubble-them"
        st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input form
    with st.form("msg_form", clear_on_submit=True):
        col1, col2 = st.columns([9, 1])
        user_msg = col1.text_input("Type a message...", label_visibility="collapsed")
        if col2.form_submit_button("➔") and user_msg:
            st.session_state.messages.append({"role": "me", "content": user_msg})
            # If supabase is connected, you can insert here:
            # if supabase: supabase.table("messages").insert({"content": user_msg, "role": "me"}).execute()
            st.rerun()

elif st.session_state.view == "Veda":
    if st.button("← Back to Chat"):
        st.session_state.view = "Chat"
        st.rerun()
    
    st.markdown(f"""
        <iframe src="{AI_LINK}" 
        style="width:100%; height:80vh; border:none; border-radius:15px; box-shadow: 0 0 15px #9d4edd;">
        </iframe>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">VibeLine ⚡ Powered by VEDA 3.0 Ultra India</div>', unsafe_allow_html=True)
