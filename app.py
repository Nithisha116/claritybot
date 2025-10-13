
import streamlit as st
import requests
import json
import time

# --- IMPORTANT: GEMINI API KEY SETUP ---
# THIS KEY IS NOW HARDCODED, WHICH IS NECESSARY FOR COLAB LAUNCHER
API_KEY = "AIzaSyC9W_vBf6xKLHpP1vbhmtc92v1NWhL1CS0"
# --- END API KEY SETUP ---

MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- APP SETUP ---

st.set_page_config(page_title="ClarityBot: Mental Wellness Assistant", layout="centered")

st.title("ClarityBot: Your AI Wellness Check-in")
st.markdown("""
<style>
    /* FIXED: Using triple quotes for the multiline string to avoid 'invalid decimal literal' SyntaxError */
    .reportview-container { background: #f0f2f6; }
    .chat-container { padding: 10px; border-radius: 10px; background-color: #ffffff; }
    .stButton>button { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 8px; }
    .stTextInput>div>div>input { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a friendly welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm ClarityBot, an AI wellness coach. I'm here to listen, offer coping strategies, and provide non-medical, empathetic support. How are you feeling today?"
    })

# --- API CALL FUNCTION WITH EXPONENTIAL BACKOFF ---

def generate_response(prompt_text, history):
    # System instruction to define the bot's persona (Crucial for an AI wellness app)
    system_prompt = (
        "You are ClarityBot, a compassionate and non-judgmental AI mental wellness coach. "
        "Your purpose is to provide empathetic listening, suggest general coping mechanisms "
        "like deep breathing or journaling, and encourage users to seek professional help "
        "if they indicate a crisis. DO NOT provide medical advice, diagnosis, or crisis "
        "intervention (just gently suggest contacting a professional helpline). "
        "Keep responses supportive, brief, and focused on the user's emotional state."
    )

    # Convert history into the required API format
    chat_history = []
    for message in history:
        role = "user" if message["role"] == "user" else "model"
        chat_history.append({"role": role, "parts": [{"text": message["content"]}]})

    chat_history.append({"role": "user", "parts": [{"text": prompt_text}]})

    payload = {
        "contents": chat_history,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }

    headers = {'Content-Type': 'application/json'}
    max_retries = 3
    delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=15)
            response.raise_for_status()

            result = response.json()
            candidate = result.get('candidates', [{}])[0]

            if not candidate or 'text' not in candidate.get('content', {}).get('parts', [{}])[0]:
                return "I seem to be having trouble processing that right now. Could you rephrase it?"

            return candidate['content']['parts'][0]['text']

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # If the 403 error still occurs, inform the user about the key
                return "HTTP Error: 403 Client Error: Forbidden. The API key is rejected. Please verify the key in the code."

            if attempt < max_retries - 1 and e.response.status_code in [429, 500, 503]:
                time.sleep(delay)
                delay *= 2
                continue

            return f"An API error occurred: {e}. Please try again."

        except requests.exceptions.RequestException as e:
            return f"A connection error occurred: {e}."

    return "I'm still unable to connect to the AI service after multiple tries."


# --- STREAMLIT UI LOGIC ---

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input prompt
if prompt := st.chat_input("What's on your mind?"):

    # 1. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI response and display loading state
    with st.chat_message("assistant"):
        with st.spinner("ClarityBot is listening..."):
            response = generate_response(prompt, st.session_state.messages)

        # 3. Add assistant response to chat history
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Button to clear history
if st.button("🔄 Clear Conversation"):
    st.session_state.messages = []
    # Re-add the welcome message upon clearing
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Conversation cleared! How can I support you now? Remember, I'm here to listen."
    })
    st.rerun()
