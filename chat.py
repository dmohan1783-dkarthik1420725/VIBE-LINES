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
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'view' not in st.session_state:
    st.session_state.view = "Chat"
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None

# --- 3. DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

# --- 4. CUSTOM CSS (Light Blue Branding) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b141a; color: white; }}
    .chat-bubble-me {{ 
        background-color: #005c4b; padding: 12px; border-radius: 15px 2px 15px 15px; 
        margin: 8px; float: right; width: 70%; border: 1px solid #128c7e; color: white; 
    }}
    .chat-bubble-them {{ 
        background-color: #202c33; padding: 12px; border-radius: 2px 15px 15px 15px; 
        margin: 8px; float: left; width: 70%; border: 1px solid #3b4a54; color: white; 
    }}
    .meta-ring {{
        width: 100px; height: 100px;
        background: linear-gradient(45deg, #00d2ff, #9d4edd, #00d2ff);
        background-size: 200% 200%;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        animation: gradient-move 3s ease infinite;
        margin: 0 auto;
    }}
    @keyframes gradient-move {{ 0% {{background-position:0% 50%}} 50% {{background-position:100% 50%}} 100% {{background-position:0% 50%}} }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; color: gray; font-size: 11px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SPLASH SCREEN & LOGIN ---
if not st.session_state.initialized:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f'<div class="meta-ring"><img src="{LOGO_URL}" width="60"></div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00d2ff; letter-spacing: 3px;'>VIBE LINE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>POWERED BY VEDA 3.0 ULTRA</p>", unsafe_allow_html=True)
        time.sleep(2)
    placeholder.empty()
    st.session_state.initialized = True

if st.session_state.user_phone is None:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>Login to VibeLine</h3>", unsafe_allow_html=True)
        with st.form("login"):
            u_name = st.text_input("Full Name")
            u_phone = st.text_input("Mobile Number")
            if st.form_submit_button("Enter App"):
                if u_name and u_phone:
                    st.session_state.user_phone = u_phone
                    st.session_state.user_name = u_name
                    if supabase:
                        supabase.table("veda_users").upsert({"phone_number": u_phone, "user_name": u_name}).execute()
                    st.rerun()
    st.stop()

# --- 6. SIDEBAR (Contacts & Add Contact) ---
with st.sidebar:
    st.markdown(f"<h2 style='color: #00d2ff;'>VibeLine</h2>", unsafe_allow_html=True)
    if st.button("🔱 Launch VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    with st.expander("➕ Add New Contact"):
        with st.form("new_contact", clear_on_submit=True):
            c_name = st.text_input("Name")
            c_code = st.selectbox("Country", ["+91 INDIA", "+1 USA", "+44 UK"])
            c_phone = st.text_input("Phone Number")
            if st.form_submit_button("Save"):
                if supabase and c_name and c_phone:
                    supabase.table("veda_contacts").insert({
                        "owner_phone": st.session_state.user_phone,
                        "contact_name": c_name,
                        "contact_phone": c_phone,
                        "country_code": c_code
                    }).execute()
                    st.rerun()

    st.caption("YOUR CHATS")
    if supabase:
        res = supabase.table("veda_contacts").select("*").eq("owner_phone", st.session_state.user_phone).execute()
        for contact in res.data:
            if st.button(f"👤 {contact['contact_name']}", use_container_width=True):
                st.session_state.current_chat = contact['contact_name']
                st.session_state.view = "Chat"
                st.rerun()

# --- 7. MAIN CHAT AREA ---
if st.session_state.view == "Chat":
    if st.session_state.current_chat:
        st.subheader(f"💬 {st.session_state.current_chat}")
        
        # Display Messages
        chat_container = st.container()
        with chat_container:
            if supabase:
                msgs = supabase.table("messages").select("*").eq("room", st.session_state.current_chat).order("created_at").execute()
                for m in msgs.data:
                    div = "chat-bubble-me" if m["role"] == "me" else "chat-bubble-them"
                    st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

        # FIXED: Message Search/Input Bar (Visible once contact is selected)
        with st.form("msg_form", clear_on_submit=True):
            c1, c2 = st.columns([9, 1])
            txt = c1.text_input("Type a message...", label_visibility="collapsed")
            if c2.form_submit_button("➔") and txt:
                if supabase:
                    supabase.table("messages").insert({
                        "content": txt, "role": "me", "room": st.session_state.current_chat
                    }).execute()
                    st.rerun()
    else:
        st.info("Select a contact from the sidebar to start chatting!")

elif st.session_state.view == "Veda":
    if st.button("← Back"): st.session_state.view = "Chat"; st.rerun()
    st.markdown(f'<iframe src="{AI_LINK}" style="width:100%; height:80vh; border-radius:15px; border:none;"></iframe>', unsafe_allow_html=True)

st.markdown('<div class="footer">VIBE LINE ⚡ Powered by VEDA 3.0 Ultra India</div>', unsafe_allow_html=True)
