import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title="VibeLine", page_icon="🔱", layout="wide")

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

# --- 2. SESSION STATE MANAGEMENT ---
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = None
if 'view' not in st.session_state:
    st.session_state.view = "Chat"

# --- 3. LOGIN SYSTEM (Only shows if not logged in) ---
if st.session_state.user_phone is None:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #00d2ff;'>VIBE LINE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Enter your number to start chatting</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            name = st.text_input("Your Name")
            phone = st.text_input("Phone Number (e.g. 9876543210)")
            submit = st.form_submit_button("Verify & Enter")
            
            if submit and name and phone:
                # Save to Supabase so we remember this user
                if supabase:
                    supabase.table("veda_users").upsert({"phone_number": phone, "user_name": name}).execute()
                st.session_state.user_phone = phone
                st.session_state.user_name = name
                st.rerun()
    st.stop() # Stops the rest of the app from loading until login is done

# --- 4. SIDEBAR (Contacts & Add Contact) ---
with st.sidebar:
    st.markdown(f"<h2 style='color: #00d2ff;'>Hi, {st.session_state.user_name}!</h2>", unsafe_allow_html=True)
    
    if st.button("🔱 Launch VEDA AI", use_container_width=True):
        st.session_state.view = "Veda"
    
    st.write("---")
    
    # --- ADD CONTACT SECTION ---
    with st.expander("➕ Add New Contact"):
        with st.form("add_contact_form", clear_on_submit=True):
            c_name = st.text_input("Name")
            c_code = st.selectbox("Country", ["+91 INDIA", "+1 USA", "+44 UK", "+971 UAE"])
            c_phone = st.text_input("Phone Number")
            if st.form_submit_button("Save Contact"):
                if supabase:
                    supabase.table("veda_contacts").insert({
                        "owner_phone": st.session_state.user_phone,
                        "contact_name": c_name,
                        "contact_phone": c_phone,
                        "country_code": c_code
                    }).execute()
                    st.success("Saved!")
                    st.rerun()

    st.write("---")
    st.caption("YOUR CONTACTS")
    
    # Fetch real contacts from Supabase
    if supabase:
        res = supabase.table("veda_contacts").select("*").eq("owner_phone", st.session_state.user_phone).execute()
        for contact in res.data:
            if st.button(f"👤 {contact['contact_name']}", use_container_width=True):
                st.session_state.current_chat = contact['contact_name']
                st.session_state.view = "Chat"
                st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
if st.session_state.view == "Chat":
    target = getattr(st.session_state, 'current_chat', 'Select a Contact')
    st.subheader(f"💬 {target}")
    
    # (Your existing message fetching and input form goes here)
    st.info("Messages will appear here once you select a contact and start typing!")

elif st.session_state.view == "Veda":
    if st.button("← Back"):
        st.session_state.view = "Chat"
        st.rerun()
    st.markdown(f'<iframe src="https://veda-ultra-india.streamlit.app" style="width:100%; height:80vh; border-radius:15px;"></iframe>', unsafe_allow_html=True)
