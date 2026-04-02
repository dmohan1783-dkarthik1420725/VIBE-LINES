import streamlit as st
from supabase import create_client
import time

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="VibeLine", page_icon="🔱", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

# --- 2. WHATSAPP THEME CSS ---
st.markdown("""
    <style>
    /* WhatsApp Dark Mode Colors */
    .stApp { background-color: #0b141a; color: #e9edef; }
    
    /* The 3-Column Layout */
    .main-container { display: flex; height: 100vh; overflow: hidden; }
    
    /* Column 1: Slim Icon Bar */
    .icon-bar { width: 60px; background-color: #202c33; border-right: 1px solid #313d45; display: flex; flex-direction: column; align-items: center; padding-top: 20px; }
    
    /* Column 2: Contacts Bar (approx 6cm / 350px) */
    .contacts-bar { width: 350px; background-color: #111b21; border-right: 1px solid #222d34; overflow-y: auto; }
    
    /* Column 3: Chat/AI Space */
    .chat-area { flex-grow: 1; background-color: #0b141a; display: flex; flex-direction: column; }

    /* Meta-style VEDA Button */
    .veda-btn {
        background: linear-gradient(90deg, #00d2ff, #9d4edd);
        border: none; border-radius: 20px; color: white; padding: 10px;
        width: 90%; margin: 10px auto; cursor: pointer; font-weight: bold;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'user_phone' not in st.session_state: st.session_state.user_phone = None
if 'current_view' not in st.session_state: st.session_state.current_view = "Veda" # Default view

# --- 4. LOGIN CHECK ---
if st.session_state.user_phone is None:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#00d2ff;'>VIBE LINE</h1>", unsafe_allow_html=True)
        phone = st.text_input("Enter Mobile Number")
        if st.button("Enter"):
            st.session_state.user_phone = phone
            st.rerun()
    st.stop()

# --- 5. THE THREE-COLUMN INTERFACE ---
# We use st.columns to simulate the layout
c1, c2, c3 = st.columns([0.5, 3, 7])

# --- COLUMN 1: ICON BAR ---
with c1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("💬", unsafe_allow_html=True)
    st.markdown("<br>📞", unsafe_allow_html=True)
    st.markdown("<br>🎡", unsafe_allow_html=True)
    st.markdown("<br><br>⚙️", unsafe_allow_html=True)

# --- COLUMN 2: CONTACTS BAR (6cm) ---
with c2:
    st.markdown("<h3 style='margin-left:10px;'>Chats</h3>", unsafe_allow_html=True)
    
    # Meta AI Entry
    if st.button("✨ Ask VEDA 3.0 Ultra", use_container_width=True):
        st.session_state.current_view = "Veda"
        st.rerun()
    
    st.write("---")
    
    # List Contacts
    if supabase:
        contacts = supabase.table("veda_contacts").select("*").eq("owner_phone", st.session_state.user_phone).execute()
        for c in contacts.data:
            if st.button(f"👤 {c['contact_name']}", key=c['contact_phone'], use_container_width=True):
                st.session_state.current_view = "Chat"
                st.session_state.chat_target = c['contact_name']
                st.rerun()

# --- COLUMN 3: MAIN CHAT / AI AREA ---
with c3:
    if st.session_state.current_view == "Veda":
        st.markdown("<h4 style='color:#00d2ff;'>🔱 VEDA 3.0 Ultra AI</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <iframe src="https://veda-ultra-india.streamlit.app/" 
            style="width:100%; height:85vh; border:none; border-radius:15px; box-shadow: 0 0 15px rgba(0,210,255,0.3);">
            </iframe>
        """, unsafe_allow_html=True)
    
    elif st.session_state.current_view == "Chat":
        st.markdown(f"<h4>👤 {st.session_state.chat_target}</h4>", unsafe_allow_html=True)
        st.write("---")
        # Chat history and input bar logic goes here
        st.info("Message interface active. Ready for chatting!")
