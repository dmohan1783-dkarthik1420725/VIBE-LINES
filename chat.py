import streamlit as st
from supabase import create_client
import time

# --- 1. SETTINGS & LOGO ---
# Trishul Logo (Ensure this is a white/transparent PNG for best look)
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

# --- 4. CUSTOM CSS (WhatsApp/Meta Style) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; color: white; }}
    
    /* Chat Bubbles */
    .chat-bubble-me {{ background-color: #005c4b; padding: 12px; border-radius: 15px 2px 15px 15px; margin: 8px; float: right; width: 75%; border: 1px solid #128c7e; color: white; }}
    .chat-bubble-them {{ background-color: #202c33; padding: 12px; border-radius: 2px 15px 15px 15px; margin: 8px; float: left; width: 75%; border: 1px solid #3b4a54; color: white; }}
    
    /* VEDA Button Styling */
    .veda-btn-container {{
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 50px;
        border: 1px solid #3b4a54;
        margin-bottom: 20px;
    }}
    .veda-ring {{
        width: 35px; height: 35px;
        background: linear-gradient(45deg, #00d2ff, #9d4edd);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-right: 10px;
    }}
    
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #111b21; color: gray; font-size: 12px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.warning("Database not connected. Run locally or check Secrets.")

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## VibeLine")
    
    # Custom Meta-style VEDA button
    st.markdown("""<div class="veda-btn-container"><div class="veda-ring">🔱</div><div style="font-size:14px;">Ask VEDA 3.0 ULTRA</div></div>""", unsafe_allow_html=True)
    if st.button("Open VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    if st.button("💬 Messenger", use_container_width=True):
        st.session_state.view = "Chat"
    
    if st.button("Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN LOGIC: CHAT OR VEDA ---
if st.session_state.view == "Chat":
    st.title("⚡ VibeLine Messenger")
    
    # Display Messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            div_class = "chat-bubble-me" if msg["role"] == "me" else "chat-bubble-them"
            st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input Area
    with st.form("message_input", clear_on_submit=True):
        cols = st.columns([8, 1])
        user_text = cols[0].text_input("Message", label_visibility="collapsed", placeholder="Type a message...")
        if cols[1].form_submit_button("➔") and user_text:
            st.session_state.messages.append({"role": "me", "content": user_text})
            # Insert logic for Supabase here if needed
            st.rerun()

elif st.session_state.view == "Veda":
    st.button("← Back to Messages", on_click=lambda: st.session_state.update({"view": "Chat"}))
    # Open VEDA inside the app
    st.markdown(f"""
        <iframe src="{AI_LINK}" 
        style="width:100%; height:85vh; border:none; border-radius:15px; box-shadow: 0 0 15px #9d4edd;">
        </iframe>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">VibeLine ⚡ Powered by VEDA 3.0 Ultra India</div>', unsafe_allow_html=True)
