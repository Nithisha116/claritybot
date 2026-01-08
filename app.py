import streamlit as st
from google import genai
import base64

# --- CONFIGURATION ---
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"

# --- PAGE SETUP ---
st.set_page_config(page_title="ClarityBot | Wellness AI", page_icon="🌿", layout="centered")

# --- BACKGROUND FUNCTION ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64_encoded}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image not found. Please ensure 'background.jpg' is in the project folder.")

# Uncomment the line below once you have your background.jpg file ready!
# set_background("background.jpg")

# --- CUSTOM STYLING (CSS) ---
st.markdown("""
    <style>
    /* Chat Message Styling */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: rgba(255, 255, 255, 0.8) !important; /* Slight transparency for background */
    }
    
    /* Green Clear Conversation Button Styling */
    div.stButton > button:first-child {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #45a049 !important;
        color: white !important;
    }

    h1 {
        color: #2e7d32;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌿 ClarityBot")
    st.info("Your safe space for mental clarity and wellness support.")
    st.divider()
    st.caption("Note: I am an AI, not a doctor. If you are in crisis, please seek professional help.")

# --- MAIN INTERFACE ---
st.title("ClarityBot: Your Wellness Check-in")
st.write("Take a deep breath and share what's on your mind.")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": [{"text": "Hello! I'm ClarityBot, your AI wellness coach. I'm here to listen. How are you feeling today?"}]}
    ]

# Display chat history
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# --- INPUT SECTION (Button + Chat Bar) ---

# 1. Clear Conversation Button placed directly above chat input
if st.button("🔄 Clear Conversation"):
    st.session_state.messages = [
        {"role": "model", "parts": [{"text": "Hello! I'm ClarityBot. How are you feeling today?"}]}
    ]
    st.rerun()

# 2. Chat Input
if prompt := st.chat_input("Share your thoughts here..."):
    # User Message
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=st.session_state.messages,
                config={'system_instruction': 'You are a calm, empathetic wellness coach named ClarityBot. Keep responses encouraging and concise.'}
            )
            
            bot_text = response.text
            st.markdown(bot_text)
            st.session_state.messages.append({"role": "model", "parts": [{"text": bot_text}]})
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
