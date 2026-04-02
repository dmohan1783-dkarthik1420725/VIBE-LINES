import streamlit as st
from supabase import create_client
import time

# --- 1. SETTINGS & LOGO ---
# Trishul Logo
LOGO_URL = "https://img.icons8.com/ios-filled/512/FFFFFF/trident.png" 
AI_LINK = "https://veda-ultra-india.streamlit.app"

st.set_page_config(page_title="VibeLine", page_icon="🔱", layout="wide")

# --- 2. INITIALIZE SESSION STATE ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'view' not in st.session_state:
    st.session_state.view = "Chat"
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = "General Group"

# --- 3. DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

# --- 4. SPLASH SCREEN ---
if not st.session_state.initialized:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            st.image(LOGO_URL, width=150)
            st.markdown("<h1 style='text-align: center; color: white;'>VibeLine</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>from</p>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #9d4edd;'>VEDA 3.0 ULTRA</h3>", unsafe_allow_html=True)
    time.sleep(3)
    placeholder.empty()
    st.session_state.initialized = True

# --- 5. CUSTOM WHATSAPP CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; color: white; }}
    
    /* Meta-style VEDA Button */
    .veda-btn-container {{
        display: flex;
        align-items: center;
        background: linear-gradient(90deg, rgba(157, 78, 237, 0.2), rgba(0, 210, 255, 0.1));
        padding: 12px;
        border-radius: 50px;
        border: 1px solid #9d4edd;
        margin-bottom: 25px;
        cursor: pointer;
    }}
    
    /* Chat Bubbles */
    .chat-bubble-me {{ 
        background-color: #005c4b; padding: 12px; border-radius: 15px 2px 15px 15px; 
        margin: 8px; float: right; width: 70%; border: 1px solid #128c7e; color: white; 
    }}
    .chat-bubble-them {{ 
        background-color: #202c33; padding: 12px; border-radius: 2px 15px 15px 15px; 
        margin: 8px; float: left; width: 70%; border: 1px solid #3b4a54; color: white; 
    }}
    
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #111b21; color: gray; font-size: 12px; z-index: 99; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>VibeLine</h2>", unsafe_allow_html=True)
    
    # Meta AI Entry Point
    st.markdown('<div class="veda-btn-container"><div style="font-size:14px; width:100%; text-align:center;">🔱 Ask VEDA 3.0 ULTRA</div></div>', unsafe_allow_html=True)
    if st.button("Launch VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    st.caption("CHATS")
    
    # Group and Personal Chat Options
    chat_rooms = ["General Group", "Family Chat", "School Project", "Developers"]
    for room in chat_rooms:
        if st.button(f"💬 {room}", use_container_width=True):
            st.session_state.current_chat = room
            st.session_state.view = "Chat"
            st.rerun()

# --- 7. MAIN INTERFACE ---
if st.session_state.view == "Chat":
    st.subheader(f"⚡ {st.session_state.current_chat}")
    
    # Fetch and Display Messages
    if supabase:
        try:
            response = supabase.table("messages").select("*").eq("room", st.session_state.current_chat).order("created_at").execute()
            messages = response.data
            
            for msg in messages:
                div_class = "chat-bubble-me" if msg["role"] == "me" else "chat-bubble-them"
                st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        except Exception:
            st.error("Could not load messages. Check your SQL table!")

    # Fixed Message Input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([9, 1])
        user_input = col1.text_input("Type a message...", label_visibility="collapsed")
        if col2.form_submit_button("➔") and user_input:
            if supabase:
                supabase.table("messages").insert({
                    "content": user_input, 
                    "role": "me", 
                    "room": st.session_state.current_chat
                }).execute()
                st.rerun()

# --- 8. VEDA AI VIEW ---
elif st.session_state.view == "Veda":
    st.button("← Back to Messages", on_click=lambda: st.session_state.update({"view": "Chat"}))
    st.markdown(f"""
        <iframe src="{AI_LINK}" 
        style="width:100%; height:85vh; border:none; border-radius:15px; box-shadow: 0 0 20px #9d4edd;">
        </iframe>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">VibeLine ⚡ Secured by VEDA 3.0 Ultra India</div>', unsafe_allow_html=True)
