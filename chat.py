import streamlit as st
from supabase import create_client
import time
from datetime import datetime

# --- 1. CONFIG & LOGO ---
LOGO_URL = "https://img.icons8.com/ios-filled/512/FFFFFF/trident.png" 
AI_LINK = "https://veda-ultra-india.streamlit.app"

st.set_page_config(page_title="VibeLine ⚡", page_icon="🔱", layout="wide")

# --- 2. SESSION STATE (The Brain) ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'view' not in st.session_state:
    st.session_state.view = "Chat"
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = "General Group"

# --- 3. SUPABASE CONN ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- 4. WHATSAPP UI CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; }}
    
    /* Meta-AI Glow Ring */
    .veda-ring {{
        width: 38px; height: 38px;
        background: linear-gradient(45deg, #00d2ff, #a2d2ff, #9d4edd);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 12px rgba(157, 78, 237, 0.6);
        animation: rotate-gradient 4s linear infinite;
    }}
    
    /* WhatsApp Bubbles */
    .chat-bubble {{
        padding: 10px 15px;
        margin: 5px;
        max-width: 70%;
        font-size: 15px;
        position: relative;
    }}
    .me {{ 
        background-color: #005c4b; color: white; align-self: flex-end; 
        border-radius: 15px 0px 15px 15px; margin-left: auto;
    }}
    .them {{ 
        background-color: #202c33; color: white; align-self: flex-start; 
        border-radius: 0px 15px 15px 15px; margin-right: auto;
    }}
    .timestamp {{ font-size: 10px; color: #8696a0; margin-top: 5px; text-align: right; }}
    
    /* Hide Streamlit Header */
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR (Contact List) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>VibeLine</h2>", unsafe_allow_html=True)
    
    # Meta AI Integration
    st.markdown('<div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">', unsafe_allow_html=True)
    if st.button("🔱 Ask VEDA 3.0 ULTRA", use_container_width=True):
        st.session_state.view = "Veda"
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.caption("CHATS")
    
    # Contact List
    chats = {
        "General Group": "🌐",
        "Family": "🏠",
        "School Friends": "📚",
        "Developers": "👨‍💻"
    }
    
    for name, icon in chats.items():
        if st.button(f"{icon} {name}", key=name, use_container_width=True):
            st.session_state.current_chat = name
            st.session_state.view = "Chat"
            st.rerun()

# --- 6. MAIN CHAT INTERFACE ---
if st.session_state.view == "Chat":
    # Header
    st.markdown(f"### {st.session_state.current_chat}")
    st.write("---")

    # Fetch Messages from Supabase
    response = supabase.table("messages").select("*").eq("room", st.session_state.current_chat).order("created_at").execute()
    messages = response.data

    # Display Messages
    for msg in messages:
        style = "me" if msg['role'] == "user" else "them"
        st.markdown(f"""
            <div class="chat-bubble {style}">
                {msg['content']}
                <div class="timestamp">{msg['created_at'][11:16]}</div>
            </div>
        """, unsafe_allow_html=True)

    # Input Bar (Fixed at bottom)
    with st.container():
        st.write("") # Spacer
        with st.form("send_msg", clear_on_submit=True):
            col1, col2, col3 = st.columns([0.5, 8, 1])
            col1.markdown("➕") # Attachment icon placeholder
            u_text = col2.text_input("Type a message", label_visibility="collapsed")
            if col3.form_submit_button("➔") and u_text:
                # Save to Supabase
                supabase.table("messages").insert({
                    "content": u_text,
                    "role": "user",
                    "room": st.session_state.current_chat
                }).execute()
                st.rerun()

# --- 7. VEDA AI (Integrated) ---
elif st.session_state.view == "Veda":
    st.button("← Back", on_click=lambda: st.session_state.update({"view": "Chat"}))
    st.markdown(f'<iframe src="{AI_LINK}" style="width:100%; height:85vh; border:none; border-radius:15px;"></iframe>', unsafe_allow_html=True)
