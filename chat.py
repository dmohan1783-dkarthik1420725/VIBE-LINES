import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIG & SETTINGS ---
st.set_page_config(page_title="VibeLine", page_icon="🔱", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

# --- 2. SESSION STATE ---
if 'initialized' not in st.session_state: st.session_state.initialized = False
if 'user_phone' not in st.session_state: st.session_state.user_phone = None
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'current_chat' not in st.session_state: st.session_state.current_chat = None
if 'view' not in st.session_state: st.session_state.view = "Chat"

# --- 3. WHATSAPP UI CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b141a; color: #e9edef; }
    
    /* WhatsApp Dark Theme Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111b21;
        border-right: 1px solid #222d34;
    }

    /* Message Bubbles */
    .bubble-me {
        background-color: #005c4b;
        color: #e9edef;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px 0;
        float: right;
        clear: both;
        max-width: 80%;
    }
    .bubble-them {
        background-color: #202c33;
        color: #e9edef;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px 0;
        float: left;
        clear: both;
        max-width: 80%;
    }

    /* Custom Header & Meta Style Ring */
    .meta-ring {
        width: 80px; height: 80px;
        background: linear-gradient(45deg, #00d2ff, #9d4edd, #00d2ff);
        background-size: 200% 200%;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        animation: gradient-move 3s ease infinite;
        margin: 0 auto;
    }
    @keyframes gradient-move { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SPLASH & LOGIN ---
if not st.session_state.initialized:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="meta-ring"><img src="https://img.icons8.com/ios-filled/512/FFFFFF/trident.png" width="50"></div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00d2ff; letter-spacing: 2px;'>VIBE LINE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8696a0;'>POWERED BY VEDA 3.0 ULTRA</p>", unsafe_allow_html=True)
        time.sleep(2)
    placeholder.empty()
    st.session_state.initialized = True

if st.session_state.user_phone is None:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #00d2ff;'>Welcome</h2>", unsafe_allow_html=True)
        with st.form("login"):
            name = st.text_input("Name")
            phone = st.text_input("Phone Number (+91)")
            if st.form_submit_button("Start Chatting"):
                if name and phone:
                    st.session_state.user_phone = phone
                    st.session_state.user_name = name
                    if supabase:
                        supabase.table("veda_users").upsert({"phone_number": phone, "user_name": name}).execute()
                    st.rerun()
    st.stop()

# --- 5. WHATSAPP SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #00d2ff; margin-bottom: 0;'>VibeLine</h2>", unsafe_allow_html=True)
    st.caption(f"Logged in as: {st.session_state.user_name}")
    
    # Meta AI Button (Top of list like WhatsApp)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔱 Ask VEDA 3.0 ultra", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    
    # Add Contact Feature
    with st.expander("➕ Add New Contact"):
        with st.form("add_contact", clear_on_submit=True):
            new_name = st.text_input("Contact Name")
            new_phone = st.text_input("Phone Number")
            if st.form_submit_button("Save"):
                if supabase and new_name and new_phone:
                    supabase.table("veda_contacts").insert({
                        "owner_phone": st.session_state.user_phone,
                        "contact_name": new_name,
                        "contact_phone": new_phone
                    }).execute()
                    st.rerun()

    st.write("---")
    st.caption("CHATS")
    
    # List Saved Contacts
    if supabase:
        res = supabase.table("veda_contacts").select("*").eq("owner_phone", st.session_state.user_phone).execute()
        for c in res.data:
            if st.button(f"👤 {c['contact_name']}", key=c['contact_phone'], use_container_width=True):
                st.session_state.current_chat = c['contact_name']
                st.session_state.view = "Chat"
                st.rerun()

# --- 6. MAIN CHAT INTERFACE ---
if st.session_state.view == "Veda":
    st.markdown("### 🔱 VEDA AI MODE")
    if st.button("← Back to Chats"): 
        st.session_state.view = "Chat"
        st.rerun()
    st.markdown(f'<iframe src="https://veda-ultra-india.streamlit.app" style="width:100%; height:80vh; border:none; border-radius:15px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.current_chat:
    # Chat Header
    st.markdown(f"""
        <div style="background-color: #202c33; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
            <span style="font-weight: bold; font-size: 1.1em;">👤 {st.session_state.current_chat}</span>
        </div>
    """, unsafe_allow_html=True)

    # Message Area
    chat_box = st.container()
    with chat_box:
        if supabase:
            msgs = supabase.table("messages").select("*").eq("room", st.session_state.current_chat).order("created_at").execute()
            for m in msgs.data:
                div = "bubble-me" if m["role"] == "me" else "bubble-them"
                st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    # Message Input (WhatsApp Style)
    st.write("<br><br><br>", unsafe_allow_html=True)
    with st.form("send_msg", clear_on_submit=True):
        c1, c2 = st.columns([10, 1])
        txt = c1.text_input("Type a message", label_visibility="collapsed")
        if c2.form_submit_button("➔") and txt:
            if supabase:
                supabase.table("messages").insert({
                    "content": txt, "role": "me", "room": st.session_state.current_chat
                }).execute()
                st.rerun()
else:
    # Empty State (Landing Page)
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/ios-filled/512/FFFFFF/trident.png", width=120)
        st.markdown("<h2 style='text-align: center; color: #00d2ff;'>VibeLine Desktop</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8696a0;'>Send messages securely with end-to-end cloud sync.<br>Powered by VEDA 3.0 Ultra India</p>", unsafe_allow_html=True)

st.markdown('<div style="position: fixed; bottom: 10px; width: 100%; text-align: center; color: gray; font-size: 10px;">VIBE LINE ⚡ POWERED BY VEDA AI</div>', unsafe_allow_html=True)
