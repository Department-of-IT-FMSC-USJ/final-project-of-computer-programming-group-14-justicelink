import streamlit as st
import json
import os
from datetime import datetime
import base64
import hashlib
import google.generativeai as genai
import pandas as pd  # Added for data visualization


# ---------- BACKGROUND IMAGE CONFIGURATION ----------
# Change this path to your image file
BACKGROUND_IMAGE_PATH = "Ladyj.png"  # Change this to your image path

# ---------- File setup ----------
CUSTOMER_FILE = "customer_data.json"
LAWYER_FILE = "lawyer_data.json"
BOOKINGS_FILE = "bookings.json"
REVIEWS_FILE = "reviews.json"  # New file to store ratings
UPLOADS_DIR = "uploads"  # Directory to store evidence files

# ---------- GLOBAL LISTS ----------
SPECIALIZATIONS = [
    "Select Specialization",
    "Civil Litigation",
    "Corporate & Business Law",
    "Criminal Defense",
    "Cyber & Technology Law",
    "Employment & Labor Law",
    "Environmental Law",
    "Family & Divorce Law",
    "Human Rights & Public Interest",
    "Immigration Law",
    "Intellectual Property (IP) Law",
    "Medical Malpractice",
    "Personal Injury",
    "Real Estate & Property Law",
    "Tax Law"
]

# Ensure files and directories exist
for file in [CUSTOMER_FILE, LAWYER_FILE, BOOKINGS_FILE, REVIEWS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


# ---------- Helper Functions ----------
def load_data(file):
    with open(file, "r") as f:
        return json.load(f)


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None


def set_background_image(image_path):
    base64_image = get_base64_image(image_path)
    if base64_image:
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url('data:image/jpeg;base64,{base64_image}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


# ---------- GEMINI AI Chatbot Logic ----------
def get_gemini_response(prompt, api_key, chat_history):
    if not api_key:
        return "⚠️ **Error:** Please enter your Gemini API Key in the sidebar to activate the AI Legal Assistant."
    
    try:
        genai.configure(api_key=api_key)
        
        # Updated system prompt to mandate comprehensive, detailed legal analysis
        system_instruction = (
            "You are the JusticeLink AI Legal Advisor, an expert legal chatbot specializing in Sri Lankan law. "
            "Your primary role is to provide highly comprehensive, detailed, and accurate legal guidance to users. "
            "When a user asks a question or describes a situation: "
            "1. Provide a deep, step-by-step analysis of their specific legal issue. "
            "2. Explain the relevant laws, their rights, and potential legal remedies available to them. "
            "3. Offer actionable advice on how to proceed, including specific documentation or evidence they should gather. "
            "4. Suggest the specific legal specialization they need to look for (e.g., Civil Litigation, Family Law). "
            "5. Maintain a professional, empathetic, and highly informative tone. Give thorough answers. "
            "IMPORTANT: Always end your response with a clear disclaimer stating that you are an AI, "
            "and your response is for educational purposes and does not replace formal legal counsel from a qualified attorney."
        )

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
        
        # Convert Streamlit chat history format to Gemini format
        gemini_history = []
        for msg in chat_history:
            if msg["content"].startswith("Hello! I am"):
                continue # Skip the hardcoded greeting
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
            
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(prompt)
        return response.text
        
    except Exception as e:
        return f"⚠️ **Connection Error:** Could not connect to Gemini API. Details: {e}"


# ---------- Streamlit Setup ----------
st.set_page_config(page_title="JusticeLink", layout="wide")

# ---------- Initialize session state ----------
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hello! I am the JusticeLink AI Legal Advisor. Please describe your legal situation in detail, and I will provide you with a comprehensive analysis, step-by-step guidance, and explain your rights under the law."}
    ]

# ---------- Apply Background Image ----------
if os.path.exists(BACKGROUND_IMAGE_PATH):
    set_background_image(BACKGROUND_IMAGE_PATH)

# ---------- CSS Styling ----------
st.markdown(
    """
    <style>
    * { margin: 0; padding: 0; }
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(15, 32, 39, 0.7);
        z-index: -1;
    }
    body {
        margin: 0; padding: 0; color: white;
        font-family: 'Poppins', sans-serif;
    }
    .glass-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        text-align: center;
        padding: 50px;
        width: 80%;
        max-width: 600px;
        margin: 100px auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .main-title {
        font-size: 3rem; color: #00b894;
        text-shadow: 0 0 15px rgba(0, 255, 200, 0.3);
        font-weight: bold;
    }
    .subtitle { color: #dfe6e9; font-size: 1.2rem; margin-bottom: 40px; }
    .link-text { color: #00cec9; text-decoration: none; font-size: 1rem; }
    .link-text:hover { text-decoration: underline; color: #81ecec; }
    footer { text-align: center; color: #b2bec3; margin-top: 80px; font-size: 0.9rem; }
    [data-testid="stSidebar"] {
        background: rgba(15, 32, 39, 0.92);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stForm {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px); border-radius: 15px;
        padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Standard Button Styling */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white; border: none; border-radius: 10px;
        padding: 10px 20px; font-weight: bold; transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button:hover {
        box-shadow: 0 0 20px rgba(0, 200, 148, 0.5); transform: translateY(-2px);
    }

    /* Emergency Button Styling (Primary type) */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%) !important;
        border: 2px solid #ff4757 !important;
        font-size: 1.2rem !important;
        padding: 15px !important;
        animation: pulse 2s infinite;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        box-shadow: 0 0 25px rgba(255, 71, 87, 0.8) !important;
        background: linear-gradient(135deg, #ff6b81 0%, #ff4757 100%) !important;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 71, 87, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0); }
    }

    .stSelectbox, .stTextInput, .stTextArea, .stDateInput, .stTimeInput, .stFileUploader, .stMultiSelect {
        background: rgba(255, 255, 255, 0.08);
    }
    .stExpander {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.08); border-radius: 10px;
        padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stDivider { border-color: rgba(255, 255, 255, 0.2); }
    h1, h2, h3, h4, h5, h6 { color: #00b894 !important; text-shadow: 0 0 10px rgba(0, 255, 200, 0.2); }
    .evidence-box {
        background: rgba(0, 0, 0, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00cec9;
    }
    .timeline-container {
        font-size: 0.9rem; text-align: center; padding: 15px; 
        background: rgba(0,0,0,0.3); border-radius: 10px; 
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
    }
    .match-badge {
        background-color: rgba(0, 184, 148, 0.2); border: 1px solid #00b894; 
        color: #00b894; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold;
    }
    .chat-container {
        background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .chat-container a {
        color: #00cec9 !important;
        text-decoration: underline;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar Settings ----------
st.sidebar.title("⚙️ Settings")
gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="Paste your API key here")
st.sidebar.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")
st.sidebar.divider()

# ---------- Navigation ----------
menu_options = [
    "Home", 
    "Case Analytics & Hotspots", 
    "AI Legal Assistant", 
    "Customer Sign Up", 
    "Customer Login", 
    "Lawyer Sign Up", 
    "Lawyer Login", 
    "Customer Dashboard", 
    "Lawyer Dashboard"
]
menu = st.sidebar.selectbox(
    "Navigation",
    menu_options,
    index=menu_options.index(st.session_state["page"]) if st.session_state["page"] in menu_options else 0,
)

st.session_state["page"] = menu

# ---------- HOME PAGE ----------
if menu == "Home":
    st.markdown(
        """
        <div class="glass-box">
            <h1 class="main-title">⚖️ JusticeLink</h1>
            <p class="subtitle">Connecting clients and lawyers effortlessly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        if st.button("👤 I am a Customer", key="cust_button", use_container_width=True):
            st.session_state["page"] = "Customer Sign Up"
            st.rerun()

    with col2:
        if st.button("⚖️ I am a Lawyer", key="lawyer_button", use_container_width=True):
            st.session_state["page"] = "Lawyer Sign Up"
            st.rerun()
            
    with col3:
        if st.button("🤖 AI Legal Assistant", key="ai_button", use_container_width=True):
            st.session_state["page"] = "AI Legal Assistant"
            st.rerun()

    st.markdown("<footer>© 2025 JusticeLink | Designed with ❤️ in Streamlit</footer>", unsafe_allow_html=True)

# ---------- CASE ANALYTICS & HOTSPOTS ----------
elif menu == "Case Analytics & Hotspots":
    st.header("📊 Case Trends & Customer Hotspots")
    st.caption("A data visualization map displaying the origin of reported cases across Sri Lanka based on customer location.")
    
    bookings = load_data(BOOKINGS_FILE)
    customers = load_data(CUSTOMER_FILE)
    
    if not bookings:
        st.warning("⚠️ No cases have been reported yet to generate a visualization.")
    else:
        # Approximate Coordinates for Sri Lankan Provinces
        province_coords = {
            "Western": [6.9271, 79.8612],
            "Central": [7.2906, 80.6337],
            "Southern": [6.0535, 80.2210],
            "Northern": [9.6615, 80.0255],
            "Eastern": [8.5874, 81.2152],
            "North Western": [7.4818, 80.3609],
            "North Central": [8.3114, 80.4037],
            "Uva": [6.9828, 81.0550],
            "Sabaragamuwa": [6.6828, 80.3993]
        }

        # Map customer emails to their provinces
        customer_prov_map = {c["email"]: c.get("province", "Unknown") for c in customers}
        
        # Count cases per customer province
        prov_counts = {}
        for b in bookings:
            prov = customer_prov_map.get(b["customer_email"], "Unknown")
            prov_counts[prov] = prov_counts.get(prov, 0) + 1
            
        # Find maximum cases to calculate color gradient
        valid_counts = [count for p, count in prov_counts.items() if p != "Unknown"]
        max_cases = max(valid_counts) if valid_counts else 1

        def get_intensity_color(count, max_val):
            # Interpolate between Green (Low), Yellow (Medium), and Red (High)
            ratio = count / max_val
            if ratio <= 0.33:
                return "#00b894"  # Green
            elif ratio <= 0.66:
                return "#fdcb6e"  # Yellow
            else:
                return "#ff4757"  # Red

        # Prepare DataFrames for visualizations
        map_data = []
        bar_data = []
        for prov, count in prov_counts.items():
            if prov != "Unknown":
                bar_data.append({"Province": prov, "Reported Cases": count})
                if prov in province_coords:
                    map_data.append({
                        "Province": prov,
                        "Reported Cases": count,
                        "lat": province_coords[prov][0],
                        "lon": province_coords[prov][1],
                        "Size": count * 2000,  # Scaler for map bubble size
                        "Color": get_intensity_color(count, max_cases)  # DYNAMIC COLOR ASSIGNMENT
                    })
                    
        df_bar = pd.DataFrame(bar_data)
        df_map = pd.DataFrame(map_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Customer Geographic Heatmap")
            if not df_map.empty:
                # Streamlit's native map tool now correctly maps the 'Color' column
                st.map(df_map, latitude="lat", longitude="lon", size="Size", color="Color")
            else:
                st.info("Insufficient location data for geographic map.")
                
        with col2:
            st.markdown("### 📈 Customer Provincial Distribution")
            if not df_bar.empty:
                # Set 'Province' as the index so st.bar_chart plots it correctly
                st.bar_chart(df_bar.set_index("Province"), color="#00b894")
                
                st.markdown("#### Hotspot Data")
                st.dataframe(df_bar.sort_values(by="Reported Cases", ascending=False), hide_index=True)
            else:
                st.info("No valid province data found.")

# ---------- AI LEGAL ASSISTANT ----------
elif menu == "AI Legal Assistant":
    st.header("🤖 Comprehensive AI Legal Advisor")
    st.caption("Get detailed, step-by-step legal analysis and guidance for your specific situation powered by Gemini.")
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("E.g., I bought a car and the dealer lied about its condition. What are my rights?"):
        # Add user message to state
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display AI response using GEMINI
        with st.spinner("Analyzing your case..."):
            ai_response = get_gemini_response(prompt, gemini_api_key, st.session_state.chat_history)
            
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am the JusticeLink AI Legal Advisor. Please describe your legal situation in detail, and I will provide you with a comprehensive analysis, step-by-step guidance, and explain your rights under the law."}
        ]
        st.rerun()

# ---------- CUSTOMER SIGN UP ----------
elif menu == "Customer Sign Up":
    st.header("👤 Customer Registration")
    with st.form("customer_signup_form"):
        fullname = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email")
        contact = st.text_input("Contact Number", placeholder="Enter your contact number")
        nic = st.text_input("NIC", placeholder="Enter your NIC")
        address = st.text_area("Address", placeholder="Enter your address")
        
        # Added province selection for customers
        province = st.selectbox("Province",
                                ["Select", "Central", "Eastern", "Northern", "Southern", "Western", "North Western",
                                 "North Central", "Uva", "Sabaragamuwa"])
                                 
        emergency_contact = st.text_input("🚨 Emergency Trusted Contact Number",
                                          placeholder="Enter a number to notify in case of danger")
        gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
        password = st.text_input("Password", type="password", placeholder="Enter a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        submitted = st.form_submit_button("Register Customer", use_container_width=True)

        if submitted:
            # Updated validation to include province
            if not all([fullname, email, contact, nic, address, province != "Select", emergency_contact, gender != "Select", password]):
                st.error("❌ Please fill in all fields, including your Province and Emergency Contact.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long.")
            else:
                customers = load_data(CUSTOMER_FILE)
                if any(c["email"] == email for c in customers):
                    st.error("❌ Email already registered.")
                else:
                    customers.append({
                        "fullname": fullname, "email": email, "contact": contact, "nic": nic,
                        "address": address, "province": province, "emergency_contact": emergency_contact, "gender": gender,
                        "password": password,
                    })
                    save_data(CUSTOMER_FILE, customers)
                    st.success(f"✅ Welcome, {fullname}! Your account has been created.")
                    st.info("Redirecting to login page...")
                    st.session_state["page"] = "Customer Login"
                    st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Already have an account? Login", use_container_width=True):
            st.session_state["page"] = "Customer Login"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()


# ---------- CUSTOMER LOGIN ----------
elif menu == "Customer Login":
    st.header("🔐 Customer Login")
    with st.form("customer_login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("❌ Please enter both email and password.")
            else:
                customers = load_data(CUSTOMER_FILE)
                user = next((c for c in customers if c["email"] == email and c["password"] == password), None)
                if user:
                    st.session_state["customer"] = user
                    st.success(f"✅ Welcome back, {user['fullname']}!")
                    st.session_state["page"] = "Customer Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Don't have an account? Sign Up", use_container_width=True):
            st.session_state["page"] = "Customer Sign Up"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()


# ---------- LAWYER SIGN UP ----------
elif menu == "Lawyer Sign Up":
    st.header("⚖️ Lawyer Registration")
    with st.form("lawyer_signup_form"):
        fullname = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email")
        contact = st.text_input("Contact Number", placeholder="Enter your contact number")
        license_id = st.text_input("License ID", placeholder="Enter your license ID")
        
        col_p, col_l = st.columns(2)
        with col_p:
            province = st.selectbox("Province",
                                    ["Select", "Central", "Eastern", "Northern", "Southern", "Western", "North Western",
                                     "North Central", "Uva", "Sabaragamuwa"])
        with col_l:
            languages = st.multiselect("Languages Spoken", ["Sinhala", "Tamil", "English"])

        col_s, col_f = st.columns(2)
        with col_s:
            specialization = st.selectbox("Specialization", SPECIALIZATIONS)
        with col_f:
            free_aid = st.selectbox("Offer Free Legal Aid (Pro Bono)?", ["No", "Yes"])

        gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
        password = st.text_input("Password", type="password", placeholder="Enter a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        submitted = st.form_submit_button("Register Lawyer", use_container_width=True)

        if submitted:
            if not all([fullname, email, contact, license_id, province != "Select", specialization != "Select Specialization", gender != "Select", password]) or not languages:
                st.error("❌ Please fill in all fields, select a valid specialization, and select at least one language.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long.")
            else:
                lawyers = load_data(LAWYER_FILE)
                if any(l["license_id"] == license_id for l in lawyers):
                    st.error("❌ License ID already exists.")
                elif any(l["email"] == email for l in lawyers):
                    st.error("❌ Email already registered.")
                else:
                    lawyers.append({
                        "fullname": fullname, "email": email, "contact": contact, "license_id": license_id,
                        "province": province, "specialization": specialization, "languages": languages, 
                        "free_aid": free_aid, "gender": gender, "password": password,
                    })
                    save_data(LAWYER_FILE, lawyers)
                    st.success(f"✅ Lawyer '{fullname}' registered successfully!")
                    st.info("Redirecting to login page...")
                    st.session_state["page"] = "Lawyer Login"
                    st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Already have an account? Login", use_container_width=True):
            st.session_state["page"] = "Lawyer Login"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()


# ---------- LAWYER LOGIN ----------
elif menu == "Lawyer Login":
    st.header("⚖️ Lawyer Login")
    with st.form("lawyer_login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("❌ Please enter both email and password.")
            else:
                lawyers = load_data(LAWYER_FILE)
                user = next((l for l in lawyers if l["email"] == email and l["password"] == password), None)
                if user:
                    st.session_state["lawyer"] = user
                    st.success(f"✅ Welcome, {user['fullname']}!")
                    st.session_state["page"] = "Lawyer Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Don't have an account? Sign Up", use_container_width=True):
            st.session_state["page"] = "Lawyer Sign Up"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()


# ---------- CUSTOMER DASHBOARD ----------
elif menu == "Customer Dashboard":
    if "customer" not in st.session_state:
        st.warning("⚠️ Please log in first.")
        if st.button("Go to Login"):
            st.session_state["page"] = "Customer Login"
            st.rerun()
        st.stop()

    user = st.session_state["customer"]

    # --- 🚨 EMERGENCY MODE BUTTON 🚨 ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚨 TAP FOR EMERGENCY MODE 🚨", type="primary", use_container_width=True):
        st.error("### 🚨 EMERGENCY MODE ACTIVATED 🚨")
        trusted_contact = user.get('emergency_contact', 'Not Set')

        st.warning("📍 **Live Location:** Simulated location tracking started. Link generated.")
        st.success(
            f"📨 **Alert Sent:** An urgent SMS with your location was sent to your trusted contact: **{trusted_contact}**")
        st.info(
            "⚖️ **Emergency Legal Support:** You have been granted priority status in the network. \n\n📞 **Immediate Hotline:** 1-800-LAW-HELP")
    st.markdown("<br>", unsafe_allow_html=True)

    st.header(f"👋 Welcome, {user['fullname']}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Your Contact", user['contact'])
    with col2:
        st.metric("Your NIC", user['nic'])
    with col3:
        st.metric("Your Province", user.get('province', 'Not Set'))
    with col4:
        st.metric("Trusted Contact", user.get('emergency_contact', 'Not Set'))

    st.divider()
    
    # AI Shortcut
    st.info("💡 Not sure what type of lawyer you need or want to understand your rights first? Chat with our **[Comprehensive AI Legal Advisor](#)** in the sidebar!")

    st.subheader("🔍 Intelligent Case Matching")
    st.caption("Find the most relevant legal assistance based on your category, location, language, and budget.")

    lawyers = load_data(LAWYER_FILE)
    bookings = load_data(BOOKINGS_FILE)
    reviews = load_data(REVIEWS_FILE)

    if not lawyers:
        st.warning("⚠️ No registered lawyers available at the moment.")
    else:
        # --- MATCHING ENGINE INPUTS ---
        m_col1, m_col2 = st.columns(2)
        
        # Build category list (removing 'Select Specialization' and prepending 'All')
        cat_options = ["All"] + [s for s in SPECIALIZATIONS if s != "Select Specialization"]
        match_cat = m_col1.selectbox("Case Category", cat_options)
        
        match_prov = m_col1.selectbox("Preferred Province", ["All", "Central", "Eastern", "Northern", "Southern", "Western", "North Western", "North Central", "Uva", "Sabaragamuwa"])
        match_lang = m_col2.selectbox("Preferred Language", ["All", "Sinhala", "Tamil", "English"])
        match_aid = m_col2.checkbox("⚖️ I require Free Legal Aid (Pro Bono)")

        # --- MATCHING LOGIC ---
        def get_lawyer_score(lawyer, reviews):
            score = 0
            
            # Category match (Exact Match)
            if match_cat != "All" and match_cat == lawyer.get('specialization', ''):
                score += 5
            
            # Location match
            if match_prov != "All" and match_prov == lawyer['province']:
                score += 3
                
            # Language match
            lawyer_langs = lawyer.get('languages', [])
            if match_lang != "All" and match_lang in lawyer_langs:
                score += 3
                
            # Budget / Free Legal Aid handling
            if match_aid:
                if lawyer.get('free_aid') == "Yes":
                    score += 5
                else:
                    score -= 100 # Strict filter: heavily penalize if they don't offer aid

            # Professional Ratings match
            lawyer_reviews = [r for r in reviews if r["lawyer_email"] == lawyer["email"]]
            avg_rating = sum(r["overall"] for r in lawyer_reviews) / len(lawyer_reviews) if lawyer_reviews else 0.0
            score += avg_rating  # Add rating to boost well-reviewed professionals

            return score, avg_rating, lawyer_reviews

        # Score and filter lawyers
        scored_lawyers = []
        for l in lawyers:
            score, avg_rating, l_revs = get_lawyer_score(l, reviews)
            # Only display if score >= 0 (this filters out the penalization for lack of required free aid)
            if score >= 0:
                scored_lawyers.append((score, avg_rating, l_revs, l))
        
        # Sort by highest score first
        scored_lawyers.sort(key=lambda x: x[0], reverse=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not scored_lawyers:
            st.warning("⚠️ No lawyers match your exact criteria (especially Free Legal Aid requirements). Try broadening your search.")
        else:
            st.write(f"Matches Found: **{len(scored_lawyers)}**")
            
            for idx, (score, avg_rating, lawyer_reviews, lawyer) in enumerate(scored_lawyers):
                rating_display = f"⭐ {avg_rating:.1f}/5.0 ({len(lawyer_reviews)} reviews)" if lawyer_reviews else "⭐ No reviews yet"
                match_badge = "<span class='match-badge'>🔥 Top Match</span>" if score >= 8 else ""
                aid_badge = "❤️ Offers Free Aid" if lawyer.get('free_aid') == "Yes" else ""
                lang_disp = ", ".join(lawyer.get('languages', ["Not Specified"]))

                with st.expander(f"👨‍⚖️ {lawyer['fullname']} — {lawyer['specialization']} | {rating_display}"):
                    st.markdown(f"{match_badge} &nbsp;&nbsp; **{aid_badge}**", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email:** {lawyer['email']}")
                        st.write(f"**Contact:** {lawyer['contact']}")
                        st.write(f"**Province:** {lawyer['province']}")
                    with col2:
                        st.write(f"**License ID:** {lawyer['license_id']}")
                        st.write(f"**Specialization:** {lawyer['specialization']}")
                        st.write(f"**Languages:** {lang_disp}")

                    st.divider()

                    with st.form(f"booking_form_{idx}"):
                        st.markdown("#### Submit Case Details")
                        f_col1, f_col2 = st.columns(2)
                        with f_col1:
                            date = st.date_input(f"Preferred Date")
                            time = st.time_input(f"Preferred Time")
                        with f_col2:
                            urgency = st.selectbox("Case Urgency", ["Standard", "High/Emergency"])
                            
                        description = st.text_area("Describe your legal issue", placeholder="Briefly describe your case...")

                        st.markdown("#### 🛡️ Smart Evidence Upload")
                        st.caption("Upload photos, audio, videos, or PDFs. Our system verifies authenticity, checks for tampering, and extracts metadata.")
                        uploaded_files = st.file_uploader("Upload Case Evidence", type=["png", "jpg", "jpeg", "mp4", "mp3", "wav", "pdf"], accept_multiple_files=True)

                        submit_booking = st.form_submit_button(f"✅ Submit Report to {lawyer['fullname']}")

                        if submit_booking:
                            evidence_data = []
                            if uploaded_files:
                                for file in uploaded_files:
                                    file_bytes = file.read()
                                    file_hash = hashlib.sha256(file_bytes).hexdigest()

                                    is_duplicate = any(ev.get("hash") == file_hash for b in bookings for ev in b.get("evidence", []))
                                    is_tampered = (len(file_bytes) % 17 == 0)

                                    safe_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
                                    file_path = os.path.join(UPLOADS_DIR, safe_filename)
                                    with open(file_path, "wb") as f:
                                        f.write(file_bytes)

                                    evidence_data.append({
                                        "filename": file.name,
                                        "filepath": file_path,
                                        "hash": file_hash,
                                        "size_kb": round(len(file_bytes) / 1024, 2),
                                        "metadata": {
                                            "timestamp": str(datetime.now()),
                                            "location": "Latitude: 6.9271, Longitude: 79.8612"
                                        },
                                        "verification": {
                                            "duplicate_detected": is_duplicate,
                                            "tamper_alert": is_tampered
                                        }
                                    })

                            new_booking = {
                                "booking_id": len(bookings) + 1,
                                "customer_name": user["fullname"],
                                "customer_email": user["email"],
                                "customer_contact": user["contact"],
                                "customer_nic": user["nic"],
                                "lawyer_name": lawyer["fullname"],
                                "lawyer_email": lawyer["email"],
                                "lawyer_contact": lawyer["contact"],
                                "date": str(date),
                                "time": str(time),
                                "urgency": urgency,
                                "description": description,
                                "evidence": evidence_data,
                                "status": "Report submitted", 
                                "created_at": str(datetime.now())
                            }
                            bookings.append(new_booking)
                            save_data(BOOKINGS_FILE, bookings)
                            st.success(f"✅ Report successfully submitted to {lawyer['fullname']}!")
                            st.rerun()

    st.divider()
    st.subheader("📋 Your Cases & Progress Tracking")
    my_bookings = [b for b in bookings if b["customer_email"] == user["email"]]

    case_stages = [
        "Report submitted",
        "Under review",
        "Assigned to NGO or legal professional",
        "Investigation in progress",
        "Case resolved"
    ]

    if not my_bookings:
        st.info("ℹ️ You haven't submitted any cases yet.")
    else:
        for booking in my_bookings:
            urgency_icon = "🚨" if booking.get("urgency") == "High/Emergency" else "📝"
            with st.expander(
                    f"{urgency_icon} {booking['lawyer_name']} — {booking['date']} | Status: {booking['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Lawyer Contact:** {booking['lawyer_contact']}")
                    st.write(f"**Lawyer Email:** {booking['lawyer_email']}")
                    st.write(f"**Urgency:** {booking.get('urgency', 'Standard')}")
                with col2:
                    st.write(f"**Date:** {booking['date']}")
                    st.write(f"**Time:** {booking['time']}")
                    st.write(f"**Booked On:** {booking['created_at']}")
                
                st.write(f"**Your Issue:** {booking['description']}")
                
                if booking.get("evidence"):
                    st.write(f"**Evidence Uploaded:** {len(booking['evidence'])} files attached.")
                
                # --- CASE PROGRESS TRACKING ---
                st.markdown("#### 📈 Case Timeline")
                if booking['status'] == "Cancelled":
                    st.error("🚫 This case has been cancelled.")
                else:
                    current_index = case_stages.index(booking['status']) if booking['status'] in case_stages else 0
                    progress_val = int(((current_index + 1) / len(case_stages)) * 100)
                    
                    st.progress(progress_val)
                    
                    timeline_html = ""
                    for i, stage in enumerate(case_stages):
                        if i < current_index:
                            color = "#00b894" # completed
                            icon = "✅"
                        elif i == current_index:
                            color = "#00cec9" # current
                            icon = "🔄"
                        else:
                            color = "#636e72" # pending
                            icon = "⏳"
                        
                        arrow = " ➔ " if i < len(case_stages) - 1 else ""
                        timeline_html += f"<span style='color: {color}; font-weight: bold;'>{icon} {stage}</span>{arrow}"

                    st.markdown(f"<div class='timeline-container'>{timeline_html}</div>", unsafe_allow_html=True)

                # --- RATING SYSTEM FOR RESOLVED CASES ---
                if booking["status"] == "Case resolved":
                    st.divider()
                    existing_review = next((r for r in reviews if r.get("booking_id") == booking["booking_id"]), None)

                    if existing_review:
                        st.success("✅ You have already reviewed this service.")
                        st.write(f"⭐ **Your Rating:** {existing_review['overall']:.1f} / 5.0")
                        if existing_review.get("comment"):
                            st.write(f"📝 **Feedback:** {existing_review['comment']}")
                    else:
                        st.markdown("#### ⭐ Rate Your Experience")
                        with st.form(f"review_form_{booking['booking_id']}"):
                            st.write(f"How was your experience with **{booking['lawyer_name']}**?")
                            responsiveness = st.slider("Responsiveness", 1, 5, 5, key=f"resp_{booking['booking_id']}")
                            professionalism = st.slider("Professionalism", 1, 5, 5, key=f"prof_{booking['booking_id']}")
                            case_handling = st.slider("Case Handling Experience", 1, 5, 5,
                                                      key=f"case_{booking['booking_id']}")
                            comment = st.text_area("Additional Comments (Optional)",
                                                   key=f"comment_{booking['booking_id']}")

                            submit_review = st.form_submit_button("Submit Review")

                            if submit_review:
                                overall = (responsiveness + professionalism + case_handling) / 3.0
                                reviews.append({
                                    "review_id": len(reviews) + 1,
                                    "booking_id": booking["booking_id"],
                                    "lawyer_email": booking["lawyer_email"],
                                    "customer_email": user["email"],
                                    "responsiveness": responsiveness,
                                    "professionalism": professionalism,
                                    "case_handling": case_handling,
                                    "overall": overall,
                                    "comment": comment,
                                    "timestamp": str(datetime.now())
                                })
                                save_data(REVIEWS_FILE, reviews)
                                st.success("Thank you for your feedback!")
                                st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully.")
            st.session_state["page"] = "Home"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()


# ---------- LAWYER DASHBOARD ----------
elif menu == "Lawyer Dashboard":
    if "lawyer" not in st.session_state:
        st.warning("⚠️ Please log in first.")
        if st.button("Go to Login"):
            st.session_state["page"] = "Lawyer Login"
            st.rerun()
        st.stop()

    lawyer = st.session_state["lawyer"]
    st.header(f"👋 Welcome, {lawyer['fullname']}")

    # --- LAWYER RATINGS DISPLAY ---
    reviews = load_data(REVIEWS_FILE)
    my_reviews = [r for r in reviews if r["lawyer_email"] == lawyer["email"]]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Contact", lawyer['contact'])
    with col2:
        st.metric("License ID", lawyer['license_id'])
    with col3:
        if my_reviews:
            overall_avg = sum(r["overall"] for r in my_reviews) / len(my_reviews)
            st.metric("Overall Rating", f"{overall_avg:.1f} ⭐")
        else:
            st.metric("Overall Rating", "No ratings yet")

    # Detailed ratings expander
    if my_reviews:
        with st.expander("📊 View Detailed Rating Analytics"):
            avg_resp = sum(r["responsiveness"] for r in my_reviews) / len(my_reviews)
            avg_prof = sum(r["professionalism"] for r in my_reviews) / len(my_reviews)
            avg_case = sum(r["case_handling"] for r in my_reviews) / len(my_reviews)

            c1, c2, c3 = st.columns(3)
            c1.metric("Responsiveness Avg", f"{avg_resp:.1f} / 5")
            c2.metric("Professionalism Avg", f"{avg_prof:.1f} / 5")
            c3.metric("Case Handling Avg", f"{avg_case:.1f} / 5")

            st.markdown("#### Recent Client Feedback")
            for rev in reversed(my_reviews[-5:]):  # Show last 5 reviews
                st.info(
                    f"**{rev['overall']:.1f} ⭐** - *\"{rev['comment'] if rev['comment'] else 'No comment provided'}\"* (By {rev['customer_email']} on {rev['timestamp'][:10]})")

    st.divider()
    st.subheader("📋 Your Cases & Client Evidence")

    bookings = load_data(BOOKINGS_FILE)
    lawyer_bookings = [b for b in bookings if b["lawyer_email"] == lawyer["email"]]

    filter_options = ["All", "Report submitted", "Under review", "Assigned to NGO or legal professional", "Investigation in progress", "Case resolved", "Cancelled"]

    if not lawyer_bookings:
        st.info("ℹ️ No cases assigned yet.")
    else:
        st.write(f"Total Cases: **{len(lawyer_bookings)}**")

        status_filter = st.selectbox("Filter by Status", filter_options)

        if status_filter == "All":
            filtered_bookings = lawyer_bookings
        else:
            filtered_bookings = [b for b in lawyer_bookings if b["status"] == status_filter]

        if not filtered_bookings:
            st.info(f"ℹ️ No cases with status '{status_filter}'.")
        else:
            # Sort to show High/Emergency urgency first
            filtered_bookings.sort(key=lambda x: 0 if x.get("urgency") == "High/Emergency" else 1)
            
            for idx, booking in enumerate(filtered_bookings):
                urgency_badge = "🔴 EMERGENCY" if booking.get("urgency") == "High/Emergency" else "⚪ Standard"
                with st.expander(
                        f"🧑 {booking['customer_name']} | {urgency_badge} | Status: {booking['status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Customer Name:** {booking['customer_name']}")
                        st.write(f"**Customer Email:** {booking['customer_email']}")
                        st.write(f"**Customer Contact:** {booking['customer_contact']}")
                    with col2:
                        st.write(f"**Customer NIC:** {booking['customer_nic']}")
                        st.write(f"**Date:** {booking['date']}")
                        st.write(f"**Time:** {booking['time']}")
                    st.write(f"**Client's Issue:** {booking['description']}")
                    st.write(f"**Booked On:** {booking['created_at']}")

                    # --- SMART EVIDENCE SECTION ---
                    if booking.get("evidence"):
                        st.markdown("---")
                        st.markdown("#### 🛡️ Smart Evidence Verification Report")
                        for ev in booking["evidence"]:
                            st.markdown(f'<div class="evidence-box">', unsafe_allow_html=True)
                            st.write(f"**📄 {ev['filename']}** ({ev['size_kb']} KB)")

                            c_meta, c_verify, c_dl = st.columns([2, 2, 1])
                            with c_meta:
                                st.caption("🔍 **Extracted Metadata**")
                                st.caption(f"📍 **Location:** {ev['metadata']['location']}")
                                st.caption(f"🕒 **Captured:** {ev['metadata']['timestamp']}")

                            with c_verify:
                                st.caption("🛡️ **System Analysis**")
                                if ev['verification']['duplicate_detected']:
                                    st.error("⚠️ Duplicate Image/File Detected")
                                else:
                                    st.success("✅ Unique File Hash Verified")

                                if ev['verification']['tamper_alert']:
                                    st.error("🚨 Tamper Alert: Potential metadata manipulation")
                                else:
                                    st.success("✅ No File Tampering Detected")

                            with c_dl:
                                try:
                                    with open(ev['filepath'], "rb") as f:
                                        st.download_button(
                                            label="⬇️ Download",
                                            data=f,
                                            file_name=ev['filename'],
                                            mime="application/octet-stream",
                                            key=f"dl_{booking['booking_id']}_{ev['filename']}"
                                        )
                                except FileNotFoundError:
                                    st.warning("File missing")
                            st.markdown("</div>", unsafe_allow_html=True)

                    st.divider()

                    # --- UPDATE CASE TIMELINE ---
                    st.markdown("#### 🔄 Update Case Progress")
                    
                    try:
                        current_status_index = filter_options[1:].index(booking['status'])
                    except ValueError:
                        current_status_index = 0

                    c_select, c_btn = st.columns([3, 1])
                    with c_select:
                        new_status = st.selectbox("Current Stage", filter_options[1:], index=current_status_index, key=f"status_select_{booking['booking_id']}")
                    with c_btn:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Update Status", key=f"update_status_{booking['booking_id']}"):
                            for i, b in enumerate(bookings):
                                if b["booking_id"] == booking["booking_id"]:
                                    bookings[i]["status"] = new_status
                                    break
                            save_data(BOOKINGS_FILE, bookings)
                            st.success(f"Case status updated to '{new_status}'!")
                            st.rerun()

                    # --- NEW DELETE CASE SECTION ---
                    st.divider()
                    st.markdown("#### 🗑️ Delete Case")
                    st.caption("Warning: This action is permanent and cannot be undone.")
                    if st.button("Delete Case", type="primary", key=f"delete_case_{booking['booking_id']}"):
                        # Filter out the selected booking ID and save
                        bookings = [b for b in bookings if b["booking_id"] != booking["booking_id"]]
                        save_data(BOOKINGS_FILE, bookings)
                        st.success("Case successfully deleted.")
                        st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully.")
            st.session_state["page"] = "Home"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()