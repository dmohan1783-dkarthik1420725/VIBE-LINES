import streamlit as st
from supabase import create_client
import time
from datetime import datetime

# --- 1. SETTINGS & LOGO ---
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
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            return create_client(url, key)
    except Exception:
        return None
    return None

supabase = init_connection()

# --- 4. CUSTOM CSS (WhatsApp & Meta Style) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; color: white; }}
    
    /* Splash Screen Animations */
    .meta-ring {{
        width: 120px; height: 120px;
        background: linear-gradient(45deg, #00d2ff, #9d4edd, #00d2ff);
        background-size: 200% 200%;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 30px rgba(0, 210, 255, 0.4);
        animation: gradient-move 3s ease infinite;
        margin: 0 auto;
    }}
    
    @keyframes gradient-move {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
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
    
    /* Sidebar Buttons */
    .stButton>button {{
        border-radius: 20px;
        background-color: #202c33;
        color: white;
        border: 1px solid #3b4a54;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border-color: #00d2ff;
        color: #00d2ff;
    }}

    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #111b21; color: gray; font-size: 11px; z-index: 100; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SPLASH SCREEN ---
if not st.session_state.initialized:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        # Center Branding
        st.markdown(f"""
            <div style="text-align: center;">
                <div class="meta-ring">
                    <img src="{LOGO_URL}" width="70">
                </div>
                <br>
                <h1 style="color: #00d2ff; font-family: 'Segoe UI', sans-serif; letter-spacing: 3px; margin-bottom: 0px;">VIBE LINE</h1>
                <p style="color: #8696a0; font-size: 14px; font-weight: 500; letter-spacing: 1px; margin-top: 5px;">POWERED BY VEDA 3.0 ULTRA</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Simple loading bar
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            bar.progress(i + 1)
            
    placeholder.empty()
    st.session_state.initialized = True

# --- 6. SIDEBAR (Contacts & AI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #00d2ff;'>VibeLine</h2>", unsafe_allow_html=True)
    
    # Meta AI Styled Entry
    st.markdown('<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid #00d2ff; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 10px;">🔱 Meta AI Mode</div>', unsafe_allow_html=True)
    if st.button("Launch VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    st.caption("CONTACTS")
    
    # Contact List
    contacts = [
        {"name": "General Group", "icon": "🌐"},
        {"name": "Praneetha", "icon": "👧"},
        {"name": "Dad (IAF)", "icon": "🎖️"},
        {"name": "Developers", "icon": "👨‍💻"}
    ]
    
    for c in contacts:
        if st.button(f"{c['icon']} {c['name']}", use_container_width=True):
            st.session_state.current_chat = c['name']
            st.session_state.view = "Chat"
            st.rerun()

# --- 7. MAIN INTERFACE ---
if st.session_state.view == "Chat":
    st.subheader(f"⚡ {st.session_state.current_chat}")
    st.write("---")
    
    # Message Display Area
    chat_box = st.container()
    with chat_box:
        if supabase:
            try:
                # Fetch messages for the current room
                res = supabase.table("messages").select("*").eq("room", st.session_state.current_chat).order("created_at").execute()
                for msg in res.data:
                    div = "chat-bubble-me" if msg["role"] == "me" else "chat-bubble-them"
                    st.markdown(f'<div class="{div}">{msg["content"]}</div>', unsafe_allow_html=True)
            except Exception:
                st.info("Start a conversation!")
        else:
            st.error("Database not connected. Check your Secrets!")

    # Input Form (Fixed at bottom)
    with st.form("input_area", clear_on_submit=True):
        col1, col2 = st.columns([9, 1])
        u_input = col1.text_input("Type a message...", label_visibility="collapsed")
        if col2.form_submit_button("➔") and u_input:
            if supabase:
                supabase.table("messages").insert({
                    "content": u_input, 
                    "role": "me", 
                    "room": st.session_state.current_chat
                }).execute()
                st.rerun()

# --- 8. VEDA AI VIEW ---
elif st.session_state.view == "Veda":
    if st.button("← Back to Messages"):
        st.session_state.view = "Chat"
        st.rerun()
    
    # Iframe for your AI
    st.markdown(f"""
        <iframe src="{AI_LINK}" 
        style="width:100%; height:80vh; border:none; border-radius:20px; box-shadow: 0 0 25px rgba(157, 78, 237, 0.4);">
        </iframe>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">VIBE LINE ⚡ Powered by VEDA 3.0 Ultra India</div>', unsafe_allow_html=True)
